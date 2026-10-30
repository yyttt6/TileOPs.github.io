# Benchmarks

Baseline cache progress · Ascend 950DT · snapshot 2026-10-29T15:42:51.822235+00:00

Latencies are measured baseline results. TileOPs timings are not included in this cache snapshot, so **Ratio = NaN** and TileOPs latency is **—**. This does not rate unfinished operators or claim performance acceptance.

Times are in milliseconds. Platform default clocks; 3 warmups, 15 samples and 1 GiB cache eviction. Only cache records with complete successful correctness and guard receipts are included. The most recent eligible measurement per baseline / case is shown.

[Download measurements and provenance](baseline-cache.json).

**170 operators · 1662 / 2062 workloads with a baseline · 4898 baseline measurements.**

Coverage is partial: a measured workload can still have other baselines pending. These are recorded results, not a claim that an operator is fully covered.

## Baseline coverage

| Baseline | Measurements |
| --- | ---: |
| DeepGEMM-Ascend | 11 |
| DeepSelect | 30 |
| TileKernels | 98 |
| atvc | 43 |
| catlass | 247 |
| flash-linear-attention-npu | 453 |
| ops-fft | 2 |
| ops-math | 609 |
| ops-nn | 420 |
| ops-tensor | 69 |
| ops-transformer | 570 |
| sgl-kernel-npu | 829 |
| tilelang | 163 |
| tilelang-ascend | 561 |
| vllm-ascend | 793 |

## Data

| Page | Operators | Workloads | Baseline measurements |
| --- | ---: | ---: | ---: |
| [Elementwise](elementwise.md) | 66 | 465 | 1131 |
| [RoPE](rope.md) | 5 | 23 | 55 |
| [Reduction](reduction.md) | 19 | 169 | 387 |
| [Normalization](normalization.md) | 11 | 108 | 408 |
| [Conv & Pool](conv-pool.md) | 16 | 120 | 533 |
| [GEMM](gemm.md) | 7 | 114 | 513 |
| [Quantization & Dequantization](quantization.md) | 4 | 25 | 112 |
| [Attention](attention.md) | 15 | 174 | 516 |
| [MoE](moe.md) | 7 | 72 | 150 |
| [Sampling](sampling.md) | 3 | 11 | 11 |
| [Linear Attention](linear-attention.md) | 9 | 353 | 1016 |
| [SSM](ssm.md) | 5 | 22 | 49 |
| [Other](other.md) | 3 | 6 | 17 |
