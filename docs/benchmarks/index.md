# Benchmarks

!!! info "Nightly snapshot"

    **GPU** unknown · **commit** [`unknown`](https://github.com/yyttt6/TileOPs/commit/unknown) · **run date** unknown · **137 ops**, 725 workloads
    · [nightly run](https://github.com/yyttt6/TileOPs/actions/runs/20260903T011555Z)

## Environment

| | |
| --- | --- |
| platform | `Linux-5.10.0-136.12.0.86.r1526_92.hce2.aarch64-aarch64-with-glibc2.34` |
| python | `3.9.9` |
| provider | `tilelang` |
| headline_regime | `graph` |
| harness_commit | `6735467581f8cdc3c083aaeaad90d0709ab0efb4` |
| backend_commit | `unknown` |

Not published by this run: `image`, `driver`, `cuda`, `torch`, `tilelang`.

## Method

- **One process, common inputs.** Every implementation of an op is timed on the same tensors in the same process, in forward and then reversed order so drift does not land on whichever ran last.
- **A fixed warmup and measurement budget** per implementation, reported as the median over however many samples fit in it, with L2 cleared between iterations.
- **Compilation and workspace setup excluded.**
- **Device time is what is compared** — the union of the intervals the device spent executing the call's kernels, collected through torch_npu.profiler. A run that cannot collect device activity fails rather than falling back to a different clock.

## Coverage

- **126 of 137 ops** are measured against a real alternative — a tuned library kernel or a native PyTorch op — on the identical workload. The rest run against an eager reference only, which is not a bar worth reporting a win against.
- **Absent from every table**: 3 workloads errored and 17 were skipped in this run.

[How these numbers are taken](reading.md)

## Data

| Page | Ops | Workloads |
| --- | --- | --- |
| [Attention](attention.md) | 9 | 42 |
| [Linear Attention & SSM](linear-attention.md) | 4 | 16 |
| [GEMM, MoE & Quantization](gemm-moe.md) | 5 | 32 |
| [Elementwise & Reduction](elementwise-reduction.md) | 86 | 487 |
| [Norm, Conv, Pool & Other](norm-conv-pool.md) | 33 | 148 |
