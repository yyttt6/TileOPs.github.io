# Benchmarks

Baseline cache progress · Ascend 950DT · snapshot 2026-11-04T02:57:13.983767+00:00

Latencies are measured results on Ascend 950DT with 32 AI Cores. Ratio is the fastest listed baseline time divided by TileOPs time. A verified matching TileOPs result is required; otherwise **Ratio = NaN** and TileOPs latency is **—**. A verified TileOPs timing without an eligible baseline is shown with **Ratio = NaN**. Gray ratios use torch-eager as their fastest listed alternative.

Times are in milliseconds. Platform default clocks; 3 warmups, 15 samples and 1 GiB cache eviction. Only cache records with complete successful correctness and guard receipts are included. The most recent eligible measurement per baseline / case is shown.

[Download measurements](baseline-cache.json).

**Measurement update**

- 2026-11-04: added 1135 torch-eager measurements, full correctness, physical 32 AI Cores, 15 retained raw profiler windows and verified archives. New torch rows use v3 device-task timing; other libraries retain their recorded protocols.
- DeltaNetChunk uses newly authorized six-output torch device references checked against the unchanged independent CPU oracle.
- GQA qwen35-9b-rope-float16 uses CPU generation of parameter-only inverse frequencies. Position, trigonometry, rotation and attention execute on NPU. Reported device time excludes host parameter preparation and is not end-to-end latency.

**197 operators · 1969 / 2208 workloads with a baseline · 7212 baseline measurements.**

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
| torch-eager | 1662 |
| vllm-ascend | 793 |

## Data

| Page | Operators | Workloads | Baseline measurements |
| --- | ---: | ---: | ---: |
| [Elementwise](elementwise.md) | 70 | 527 | 1937 |
| [RoPE](rope.md) | 5 | 23 | 78 |
| [Reduction](reduction.md) | 19 | 176 | 667 |
| [Normalization](normalization.md) | 11 | 117 | 549 |
| [Conv & Pool](conv-pool.md) | 16 | 120 | 709 |
| [GEMM](gemm.md) | 7 | 114 | 691 |
| [Quantization & Dequantization](quantization.md) | 10 | 71 | 193 |
| [Attention](attention.md) | 18 | 226 | 730 |
| [MoE](moe.md) | 12 | 118 | 282 |
| [Sampling](sampling.md) | 6 | 48 | 59 |
| [Linear Attention](linear-attention.md) | 9 | 374 | 1221 |
| [SSM](ssm.md) | 7 | 35 | 62 |
| [Other](other.md) | 7 | 20 | 34 |
