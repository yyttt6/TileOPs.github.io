# Adding a new op

A new op means writing code in the six places below, and the table is in the order to work
through them.

The spec goes first: it decides what the other five files contain, and in the end it is what
they are checked against. **The spec is this pipeline's input, and the other five are written
from it.**{ .keystone }

| # | File | Named in the spec by | Contents |
| --- | --- | --- | --- |
| 1 | [`src/tileops/manifest/`](https://github.com/yyttt6/TileOPs/tree/main/src/tileops/manifest)`<family>.yaml` | the key is the op's class name | the spec itself |
| 2 | [`src/tileops/ops/`](https://github.com/yyttt6/TileOPs/tree/main/src/tileops/ops)`<family>/…` | `source.op` | the op class, subclassing `Op` |
| 2 | [`src/tileops/ops/__init__.py`](https://github.com/yyttt6/TileOPs/blob/main/src/tileops/ops/__init__.py) | — | the op's name, exported |
| 3 | [`src/tileops/kernels/`](https://github.com/yyttt6/TileOPs/tree/main/src/tileops/kernels)`<family>/…` | `source.kernel` | the kernel class, subclassing `Kernel` |
| 4 | [`tests/ops/`](https://github.com/yyttt6/TileOPs/tree/main/tests/ops)`test_<name>.py` | `source.test` | the comparison against `ref_api` |
| 5 | [`benchmarks/ops/`](https://github.com/yyttt6/TileOPs/tree/main/benchmarks/ops)`bench_<name>.py` | `source.bench` | the benchmark |

`GemmFwdOp` — the plainest matmul there is — runs through all six below.

## Before you start: the Ascend build environment

🚨 **The `tilelang` this repository declares has no Ascend backend.** The declared
dependency is `tilelang>=0.1.9,<0.2.0`, which resolves to
[`tile-ai/tilelang`](https://github.com/tile-ai/tilelang) — and that package contains no
Ascend codegen at all. **Install the declared dependencies, write a kernel, and it will not
compile for NPU.**

Ascend support lives in [`tile-ai/tilelang-ascend`](https://github.com/tile-ai/tilelang-ascend).
That repository has **no `main` branch**; pick the backend path you want: `ascendc_pto`
(AscendC / PTO codegen) or `npuir` (the MLIR path). ⚠️ **Use a separate environment per
path** — a single Python process resolves `import tilelang` to exactly one of them.

⚠️ **Append to `PYTHONPATH`; do not overwrite it**:

```bash
export PYTHONPATH=/path/to/tilelang-ascend:$PYTHONPATH   # right
export PYTHONPATH=/path/to/tilelang-ascend               # wrong -- drops CANN's own python paths
```

Overwriting loses CANN's `$ASCEND_HOME_PATH/python/site-packages` and
`.../opp/built-in/op_impl/ai_core/tbe`, and compilation then fails with
`ModuleNotFoundError: No module named 'tbe'` — **an error that reads like "this operator
cannot be compiled" when it is really the environment.**

Run this check first; it catches most of the above:

```bash
python -c "
import torch, torch_npu, os, tilelang, pathlib
print('torch_npu', torch_npu.__version__, '| CANN', os.environ.get('ASCEND_HOME_PATH'))
print('NPUs', torch.npu.device_count())
root = pathlib.Path(tilelang.__file__).parent
n = len(list(root.rglob('*ascend*')))
print('tilelang ascend files', n, '->', 'OK' if n else '🚨 this tilelang has no Ascend backend')"
```

**If the last line is 0, stop here.**

## Step 1: write the spec

What the fields mean and how to write them is in [writing a spec](manifest.md). Two things
are specific to a new op.

The first is the status. A new op starts at `status: spec-only`, meaning the interface is
settled and there is no implementation yet, so validation runs L0 — the structure check —
and does not fail over the missing code.

The second is `source.kernel_map`, the one field in the spec that nothing can derive.

An op may have more than one kernel behind it: GEMM uses a matmul kernel at general
shapes, and at M = 1 the problem degenerates to a matrix-vector product that a different
kernel does faster. `kernel_map` is the roster of those kernels — a name for each, against
the Kernel class that implements it:

```yaml
GemmFwdOp:
  ref_api: torch.matmul
  family: gemm
  status: spec-only
  signature:
    inputs:
      a: {dtype: "float16 | bfloat16"}
      b: {dtype: "same_as(a)"}
    outputs:
      d: {dtype: "same_as(a)"}
    params:
      trans_a: {type: bool, default: false}
      trans_b: {type: bool, default: true}
    shape_rules:
      - "d.shape == ((a.shape[1] if trans_a else a.shape[0]), (b.shape[0] if trans_b else b.shape[1]))"
  source:
    kernel: tileops/kernels/gemm/dense.py
    kernel_map:
      gemm_kernel: GemmKernel
      gemv_kernel: GemvKernel
    op: tileops/ops/gemm/gemm.py
    test: tests/ops/test_gemm.py
    bench: benchmarks/ops/bench_gemm.py
```

Those names are how a kernel is asked for at runtime: `_eager_forward` picks one, passes
the name to `get_or_build_kernel`, and the op layer looks the class up in `kernel_map` and
builds it (see [step 2](#op-class)). An external backend registers against the same roster
— whichever name it registers a `build_kernel` for is the kernel of the op it takes over.

The names are yours to choose, they should say what the kernel is for, and once the op code
uses one it should not change: it is the word the spec, the op and any backend all agree
on. That is also why nothing can derive it — only whoever writes the kernels knows how many
cases the op splits into.

## Step 2: write the op class {#op-class}

The op class subclasses [`Op`](https://github.com/yyttt6/TileOPs/blob/main/src/tileops/ops/op_base.py) and sits between the spec and the kernel: it validates the
arguments against the spec, infers the output shapes, then fetches a kernel and launches
it. It comes first because the spec dictates all of it, and the line where it builds a
kernel is what fixes that kernel's constructor signature.

### The class, and its four members

`GemmFwdOp`'s skeleton, with the parts of each body that are beside the point elided:

```python
class GemmFwdOp(Op):
    def __init__(self, trans_a=False, trans_b=True, kernel_map=None, tune=False):
        self.trans_a, self.trans_b, self.tune = trans_a, trans_b, tune
        self.dispatch_kernel(kernel_map)             # establishes this instance's kernel_map

    @property
    def default_kernel_map(self):                    # the spec's source.kernel_map
        return {"gemm_kernel": GemmKernel, "gemv_kernel": GemvKernel}

    def _infer_output_shapes(self, a_shape, b_shape):
        m = a_shape[1] if self.trans_a else a_shape[0]
        n = b_shape[0] if self.trans_b else b_shape[1]
        return {"d": (m, n)}                         # the spec's shape_rules

    def forward(self, a, b):
        self._validate_dtypes(a, b)                  # generated by the base class
        m, n, k = self._infer_mnk(a, b)
        a, b = a.contiguous(), b.contiguous()        # handed over as the spec declares it
        slot = "gemv_kernel" if m == 1 else "gemm_kernel"
        kernel = self.get_or_build_kernel(
            slot,                                    # a name from kernel_map
            (a, b),                                  # the memo key's tensors, and what a backend receives
            key=(m, n, k, a.dtype),                  # the cache key on the in-tree side
            build=lambda: self.kernel_map[slot](m, n, k, a.dtype, tune=self.tune),
        )
        return kernel(a, b)
```

Four members to write, each of them from the spec:

| # | Member | Written from |
| --- | --- | --- |
| 1 | `__init__` | the names and defaults in `signature.params`, plus `kernel_map` and `tune`, closing with `self.dispatch_kernel(kernel_map)` to establish this instance's kernel_map |
| 2 | `default_kernel_map` | `source.kernel_map`: the same names, against the Kernel classes themselves |
| 3 | `_infer_output_shapes` | the rules in `signature.shape_rules` that derive an output's shape |
| 4 | `forward` | `signature.inputs` — its order and defaults, optional inputs last — plus the validation, the contiguity, fetching the kernel and launching it |

Two more members arrive on their own. When the subclass is defined, the base class
synthesises `_validate_dtypes` and `eval_roofline` from the spec's dtype declarations and
its `roofline`, so they are there to call — and worth overriding only where the op needs
something the spec cannot say.

### `get_or_build_kernel`

A kernel is a compiled artefact, hundreds of milliseconds to seconds to build, while an op
instance is called over and over at different shapes and dtypes. The op layer therefore
keeps a memo table: a kernel this call needs and has built before comes straight back,
and only otherwise is one built and stored. `get_or_build_kernel` is that table's only
entrance, and the point where the in-tree implementation and an external backend part
ways — the second layer of selection in [the backend protocol](backends.md).

Its four arguments:

**`name`** — which kernel this call wants, as a name from `kernel_map`.

```python
slot = "gemv_kernel" if m == 1 else "gemm_kernel"
```

The in-tree side looks up the Kernel class under that name; a backend looks up the
`build_kernel` it registered under it. An op has as many names as it has cases.

**`inputs`** — the tensors the kernel is about to be handed, in `signature.inputs` order,
one slot per input.

```python
self.get_or_build_kernel(slot, (a, b), ...)                     # GEMM: two required inputs
self.get_or_build_kernel("group_norm", (x, weight, bias), ...)  # an absent optional input is None
```

The external path keys on it — the device, plus each slot's `(dtype, shape)`. The device
counts because an artefact compiled for one card may hold resources on it. A backend's
`build_kernel` receives the same tensors as `TensorSpec`s: device, dtype, shape, no
data.

An optional input that was not passed keeps its slot, as `None`; that is what a backend
reads presence off, rather than counting slots. Squeeze the empty slots out, and a clamp
with only a lower bound looks exactly like one with only an upper bound.

Omitting `inputs` raises nothing until a backend is installed, and then
`OpNotAvailableError`: the op stays in-tree only, out of reach of any target (see [after
install: two states](backends.md#three-states)).

**`key`** — what the in-tree kernel specializes on; the in-tree path only. What becomes of
these last two once a backend serves the op is in [how one call reaches
`build_kernel`](backends.md#from-op-layer).

```python
key=(m, n, k, a.dtype)                             # GEMM: three dimensions and the dtype
key=(self._cache_key(*input_shapes), x.dtype)      # the general form
```

The default `_cache_key` takes the sizes of every non-static axis across the inputs —
always correct, but it can over-fragment: one compile per distinct shape. Where the kernel
depends on fewer quantities, override it to project the shape onto those, flattening the
leading dims to one product when the kernel treats its input as 2-D.

**`build`** — how that in-tree kernel is constructed; the in-tree path only.

```python
build=lambda: self.kernel_map[slot](m, n, k, a.dtype, tune=self.tune)
```

Called once per `key`, which is why compiling belongs here. It may return one Kernel, a
sequence of Kernels built together, or a dataclass carrying them — the last two suit an op
that launches several kernels per call.

An op with no in-tree implementation at all, one written to depend on a backend, may leave
`build` out; a call on a device no target claims then raises `OpNotAvailableError`.

### Finishing: the compile boundary, and registering

Two things to finish, a few lines each:

- **To support `torch.compile`**, declare a compile boundary as well: `forward` only calls
  the opaque operator, and the validation, the kernel lookup and the launch move into
  `_eager_forward`. The op above declares none, so its `forward` holds all the work. How to
  declare it is in [bringing an op into torch.compile](torch-compile.md).
- **Add the op's name** to the imports and `__all__` in
  [`src/tileops/ops/__init__.py`](https://github.com/yyttt6/TileOPs/blob/main/src/tileops/ops/__init__.py), or `from tileops.ops import ...` will not find it.

## Step 3: write the kernel

A kernel lives under [`src/tileops/kernels/`](https://github.com/yyttt6/TileOPs/tree/main/src/tileops/kernels) and is written in TileLang.
**In this repository a kernel is a build function registered with
[`@register`](https://github.com/yyttt6/TileOPs/blob/main/src/tileops/kernels/_registry.py), not a class subclassing a base** — it takes this
call's tensors and returns something callable:

```python
from .._registry import register

@register("GemmFwdOp")                       # the name is the op class name
def build_gemm(a, b, *, trans_a=False, trans_b=True):
    ...                                      # validation
    return build_gemm_kernel(tuple(a.shape), tuple(b.shape), a.dtype, trans_a, trans_b)
```

The op layer asks for it through `get_or_build_kernel(name, inputs)` and **never
constructs a kernel itself**.

**The build function's signature is fixed by the spec**: one positional argument per
`signature.inputs` entry in declaration order — an optional input that was not passed
arrives as `None` — then `signature.params` by keyword. What the kernel *computes* is
unconstrained: it neither reads the spec nor is checked against it, and the spec records
only its path.

The kernel body opens with `T.Kernel(..., is_npu=True)`, and splits by execution unit —
`T.Scope("C")` is the Cube, `T.Scope("V")` the Vector:

```python
with T.Kernel(launch_blocks, is_npu=True) as (cid, vid):
    with T.Scope("C"):                       # Cube: matrix multiply
        ...
    with T.Scope("V"):                       # Vector: elementwise, reductions
        ...
```

How arguments divide is a hard requirement: **only values compiled into the generated code
go into the cached builder.** Shapes, dtypes and layout flags belong there, because the
generated code treats them as constants: loop bounds, tile sizes and the shapes of the
transfer instructions all unroll from them. **The tensors do not go into the builder** —
the `@register` layer takes them, and each call swaps pointers.

Dividing them wrong costs a recompile. A decode step advances one token at a time, so
`seq_len` grows by one every step and batch changes with the running set:

```python
# wrong: seq_len in the cached builder — every step is a new kernel
kernel = build_attn_kernel(batch, seq_len, num_heads, dtype)

# right: only compile-time constants in the builder; varying sizes come off the tensors
kernel = build_attn_kernel(num_heads, head_dim, dtype)
out = kernel(q, k, v)                       # seq_len is read off the tensor shapes
```

With the first form, `seq_len` ends up in `get_or_build_kernel`'s `key`, every step misses,
every step compiles, and decode goes nowhere.

## Step 4: write the test

Tests live in [`tests/ops/`](https://github.com/yyttt6/TileOPs/tree/main/tests/ops), and what they compare against is the spec's `ref_api`, point
by point, over the shapes and dtypes the spec declares — small shapes marked `smoke` for
the PR checks, large ones `full` for the nightly.

The scaffolding is `TestBase` and `FixtureBase` from
[`tests/test_base.py`](https://github.com/yyttt6/TileOPs/blob/main/tests/test_base.py), with the cases in `PARAMS`.

Where the op has an optional input, both sides need a case — passed and not passed often
run different kernels.

🚨 **On Ascend the op must be constructed with `target="ascend"` explicitly**:

```python
op = MyFwdOp(...)
op.target = "ascend"          # this form works for every operator
```

⚠️ **Do not write `MyFwdOp(..., target="ascend")`.** `target` is a **class attribute** on
`Op`, and only some operators also accept it as a keyword in their own `__init__` -- 81 of
157 do, **76 do not**, including `AbsFwdOp`, `BmmFwdOp` and `CosFwdOp`.
**Setting the attribute works everywhere; passing it to the constructor raises `TypeError`
on nearly half of them.**

`tileops.backend.dispatch.detect_target()` returns `None` for an `npu` device — `None`
meaning "no external backend is installed for this hardware" — so an op constructed
without a target finds no kernel when it first runs. **The symptom is an entire test file
failing, which looks like the kernel does not work at all.** Every op construction in a
test needs it.

## Step 5: write the benchmark

Benchmarks live in [`benchmarks/ops/`](https://github.com/yyttt6/TileOPs/tree/main/benchmarks/ops) and subclass `ManifestBenchmark`. The shapes are not
written here: they come from the spec's `workloads` through `load_workloads(<op>)`, and
hand-written shapes fail L4 validation:

```python
from benchmarks.benchmark_base import ManifestBenchmark, workload_params
from tileops.manifest import load_workloads

_OP_NAME = "GemmFwdOp"
```

Record at least one non-TileOPs baseline as well, or the row has nothing to compare
against. Where a baseline needs its input converted, that conversion stays inside its own
timed region. What the reported numbers mean is in [how a benchmark is timed](timing.md).

## Step 6: flip the status, and let CI take over

With the other five written, check your own work with the three commands below:

```bash
python scripts/validate_manifest.py --check-op GemmFwdOp   # spec and code agree, all five levels
python -m pytest tests/ops/test_gemm.py -v                # numerics match ref_api
python -m pytest benchmarks/ops/bench_gemm.py             # the benchmark produces numbers
```

With all three passing, flip the spec's `status` from `spec-only` to `implemented`. That
one edit takes validation from L0 to all five levels and puts the op inside CI's reach:
every later change is held against the spec by the validator, the tests and the nightly
benchmark.

## Afterwards

Once the op runs, two optional things remain:

- Let the op into a user's compiled graph — [bringing an op into
  torch.compile](torch-compile.md).
- Let someone else's kernels serve it on other hardware — [adding a hardware
  backend](backends.md).
