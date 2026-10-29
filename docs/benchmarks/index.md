# Benchmarks

Baseline cache progress · Ascend 950DT · snapshot 2026-10-29T14:10:43+00:00

Latencies are measured baseline results. TileOPs timings are not included in this cache snapshot, so **Ratio = NaN** and TileOPs latency is **—**. This does not rate unfinished operators or claim performance acceptance.

Times are profiler-measured device execution times in milliseconds. Platform default clocks; 3 warmups, 15 samples and 1 GiB cache eviction. Only cache records with complete successful correctness and guard receipts are included. The most recent eligible device measurement per baseline / case is shown.

[Download measurements and provenance](baseline-cache.json).

**149 operators · 1338 / 2062 workloads with a baseline · 3111 baseline measurements.**

Coverage is partial: a measured workload can still have other baselines pending. These are recorded results, not a claim that an operator is fully covered.

## Baseline coverage

| Baseline | Measurements |
| --- | ---: |
| DeepGEMM-Ascend | 6 |
| DeepSelect | 30 |
| TileKernels | 98 |
| atvc | 43 |
| flash-linear-attention-npu | 107 |
| ops-math | 447 |
| ops-nn | 381 |
| ops-transformer | 302 |
| sgl-kernel-npu | 720 |
| tilelang | 131 |
| tilelang-ascend | 559 |
| vllm-ascend | 287 |

## Data

| Page | Operators | Workloads | Baseline measurements |
| --- | ---: | ---: | ---: |
| [Elementwise](elementwise.md) | 64 | 448 | 1047 |
| [Reduction](reduction.md) | 19 | 168 | 381 |
| [Conv & Pool](conv-pool.md) | 15 | 110 | 323 |
| [Quantization & Dequantization](quantization.md) | 4 | 25 | 95 |
| [Attention](attention.md) | 8 | 81 | 197 |
| [MoE](moe.md) | 3 | 33 | 63 |
| [Sampling](sampling.md) | 1 | 8 | 8 |
| [Linear Attention](linear-attention.md) | 6 | 254 | 315 |
| [Other](other.md) | 29 | 211 | 682 |
