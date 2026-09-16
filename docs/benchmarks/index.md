# Benchmarks

!!! info "Nightly snapshot"

    **GPU** Ascend 910B1 · **commit** [`06fc97a46e76`](https://github.com/yyttt6/TileOPs/commit/06fc97a46e7664b3f30bbee6d66e2abd1061972b) · **run date** 2026-09-15T13:40:51+00:00 · **140 ops**, 728 workloads
    · [nightly run](https://github.com/yyttt6/TileOPs/actions/runs/20260915T134051Z)

## Environment

| | |
| --- | --- |
| timer | `torch_npu_profiler_device_kernel_interval_union` |
| platform | `Linux-5.10.0-136.12.0.86.r1526_92.hce2.aarch64-aarch64-with-glibc2.34` |
| python | `3.11.13` |
| provider | `tilelang` |
| headline_regime | `graph` |
| harness_commit | `cbd7900d8b333aaf495f7477e333cb16d0e3d132` |
| backend_commit | `06fc97a46e7664b3f30bbee6d66e2abd1061972b` |
| R319_repeat_summary | `31/40 operators updated: N=5 independent processes; each workload shows the median ratio in its original graph or legacy eager regime, with the original paired timings. Other operators retain their original measurements.` |

Not published by this run: `image`, `driver`, `cuda`, `torch`, `tilelang`.

## Method

- **One process, common inputs.** Every implementation of an op is timed on the same tensors in the same process, in forward and then reversed order so drift does not land on whichever ran last.
- **A fixed warmup and measurement budget** per implementation, reported as the median over however many samples fit in it, with L2 cleared between iterations.
- **Compilation and workspace setup excluded.**
- **Device time is what is compared** — the union of the intervals the device spent executing the call's kernels, collected through torch_npu.profiler. A run that cannot collect device activity fails rather than falling back to a different clock.

## Coverage

- **127 of 140 ops** are rated against a real alternative measured on the identical workload. The denominator is the ops **this snapshot benchmarked**, not everything TileOPs declares. The rest run against an eager reference only, which is not a bar worth reporting a win against.
- **Each op is raced against a pool, not against one fixed opponent.** Every baseline the harness could build for a workload is timed on that workload, and the fastest of them becomes the baseline the ratio divides by. The row lists the whole pool, fastest first.
- **19 of 140 ops** have a tier-1 open-source baseline in their pool at all — a kernel built from the source of a third-party Ascend operator library, admitted only on evidence that the library's own compiled kernel ran. Same denominator as above. This is the **stricter** of the two readings, and the one to quote for a claim about open-source libraries.
- **22/140 ops** have a measured `tilelang-ascend` candidate (tier `tilelang_ref`) in the published pool; this count can overlap the open-source count above.
- **For the other 109 of 140**, the pool holds vendor implementations only — a CANN built-in, or torch_npu's own dispatch. Those rows are still measured against a real implementation of the op on the identical workload, but a win there is **not** a win over an open-source library. The tier badge on each line says which it was.
- **Absent from every table**: 3 workloads errored and 17 were skipped in this run.

[How these numbers are taken](reading.md)

## Data

| Page | Ops | Workloads |
| --- | --- | --- |
| [Attention](attention.md) | 12 | 45 |
| [Linear Attention & SSM](linear-attention.md) | 4 | 16 |
| [GEMM, MoE & Quantization](gemm-moe.md) | 5 | 32 |
| [Elementwise & Reduction](elementwise-reduction.md) | 86 | 487 |
| [Norm, Conv, Pool & Other](norm-conv-pool.md) | 33 | 148 |
