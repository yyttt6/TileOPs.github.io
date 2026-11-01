# Benchmarks

Baseline cache progress · Ascend 950DT · snapshot 2026-11-01T12:22:53.032329+00:00

Latencies are measured results on Ascend 950DT with 32 AI Cores. Ratio is the fastest listed baseline time divided by TileOPs time. A verified matching TileOPs result is required; otherwise **Ratio = NaN** and TileOPs latency is **—**. A verified TileOPs timing without an eligible baseline is shown with **Ratio = NaN**. Gray ratios use torch-eager as their fastest listed alternative.

Times are in milliseconds. Platform default clocks; 3 warmups, 15 samples and 1 GiB cache eviction. Only cache records with complete successful correctness and guard receipts are included. The most recent eligible measurement per baseline / case is shown.

[Download measurements](baseline-cache.json).

**172 operators · 1732 / 2208 workloads with a baseline · 6077 baseline measurements.**

**Verified TileOPs results: 70 operators · 527 workloads.**

Coverage is partial: a measured workload can still have other baselines pending. These are recorded results, not a claim that an operator is fully covered.

## Baseline coverage

| Baseline | Measurements |
| --- | ---: |
| DeepGEMM-Ascend | 58 |
| DeepSelect | 30 |
| TileKernels | 98 |
| atvc | 43 |
| catlass | 247 |
| flash-linear-attention-npu | 476 |
| ops-fft | 2 |
| ops-math | 801 |
| ops-nn | 716 |
| ops-tensor | 69 |
| ops-transformer | 600 |
| sgl-kernel-npu | 893 |
| tilelang | 163 |
| tilelang-ascend | 561 |
| torch-eager | 527 |
| vllm-ascend | 793 |

## Data

| Page | Operators | Workloads | Baseline measurements |
| --- | ---: | ---: | ---: |
| [Elementwise](elementwise.md) | 70 | 527 | 1937 |
| [RoPE](rope.md) | 5 | 23 | 55 |
| [Reduction](reduction.md) | 19 | 170 | 492 |
| [Normalization](normalization.md) | 11 | 114 | 437 |
| [Conv & Pool](conv-pool.md) | 16 | 120 | 593 |
| [GEMM](gemm.md) | 7 | 114 | 583 |
| [Quantization & Dequantization](quantization.md) | 4 | 25 | 122 |
| [Attention](attention.md) | 15 | 174 | 519 |
| [MoE](moe.md) | 7 | 72 | 164 |
| [Sampling](sampling.md) | 3 | 11 | 11 |
| [Linear Attention](linear-attention.md) | 9 | 362 | 1120 |
| [SSM](ssm.md) | 3 | 14 | 27 |
| [Other](other.md) | 3 | 6 | 17 |
