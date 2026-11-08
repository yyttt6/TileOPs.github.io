# Benchmarks

Baseline cache progress · Ascend 950DT · snapshot 2026-11-08T15:18:43.337215+00:00

Latencies are measured results on Ascend 950DT with 32 AI Cores. Ratio is the fastest listed baseline time divided by TileOPs time. A verified matching TileOPs result is required; otherwise **Ratio = NaN** and TileOPs latency is **—**. A verified TileOPs timing without an eligible baseline is shown with **Ratio = NaN**. Gray ratios use torch-eager as their fastest listed alternative.

Times are in milliseconds. Platform default clocks; 3 warmups, 15 samples and 1 GiB cache eviction. Only cache records with complete successful correctness and guard receipts are included. The most recent eligible measurement per baseline / case is shown.

[Download measurements](baseline-cache.json).

**Measurement update**

- 2026-11-07: publish 234 strictly accepted v0.1.0 torch measurements and 400 accepted native retests. Unchanged saved baselines retain their original protocol labels.
- The displayed inventory retains previously published workloads; it is not a claim of complete v0.1.0 coverage. Previous incompatible contracts are preserved in historical_rows for exact-contract CI matching.
- All new archive hashes, correctness and valid 32AIC/64AIV guard receipts verified. Fifteen-window raw replay is established by the campaign acceptance receipts.
- 2026-11-08: replace 14 torch-eager and 10 tilelang-ascend baselines with verified AICPU-free device measurements; workload contracts and existing TileOPs measurements retained.

**210 operators · 2296 / 2296 workloads with a baseline · 7735 baseline measurements.**

**Verified TileOPs results: 134 operators · 1043 workloads.**

Coverage is partial: a measured workload can still have other baselines pending. These are recorded results, not a claim that an operator is fully covered.

## Baseline coverage

| Baseline | Measurements |
| --- | ---: |
| DeepGEMM-Ascend | 58 |
| DeepSelect | 30 |
| TileKernels | 88 |
| atvc | 43 |
| catlass | 247 |
| flash-linear-attention-npu | 468 |
| ops-fft | 2 |
| ops-math | 801 |
| ops-nn | 689 |
| ops-tensor | 69 |
| ops-transformer | 582 |
| sgl-kernel-npu | 875 |
| tilelang | 163 |
| tilelang-ascend | 562 |
| torch-eager | 2296 |
| vllm-ascend | 762 |

## Data

| Page | Operators | Workloads | Baseline measurements |
| --- | ---: | ---: | ---: |
| [Elementwise](elementwise.md) | 71 | 530 | 1948 |
| [RoPE](rope.md) | 5 | 23 | 44 |
| [Reduction](reduction.md) | 19 | 178 | 670 |
| [Normalization](normalization.md) | 12 | 131 | 521 |
| [Conv & Pool](conv-pool.md) | 16 | 120 | 713 |
| [GEMM](gemm.md) | 8 | 235 | 818 |
| [Quantization & Dequantization](quantization.md) | 10 | 71 | 193 |
| [Attention](attention.md) | 24 | 310 | 799 |
| [MoE](moe.md) | 12 | 147 | 311 |
| [Sampling](sampling.md) | 6 | 48 | 59 |
| [Linear Attention](linear-attention.md) | 10 | 415 | 1527 |
| [SSM](ssm.md) | 10 | 54 | 81 |
| [Other](other.md) | 7 | 34 | 51 |
