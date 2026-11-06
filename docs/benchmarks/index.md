# Benchmarks

Baseline cache progress · Ascend 950DT · snapshot 2026-11-06T06:32:09.125728+00:00

Latencies are measured results on Ascend 950DT with 32 AI Cores. Ratio is the fastest listed baseline time divided by TileOPs time. A verified matching TileOPs result is required; otherwise **Ratio = NaN** and TileOPs latency is **—**. A verified TileOPs timing without an eligible baseline is shown with **Ratio = NaN**. Gray ratios use torch-eager as their fastest listed alternative.

Times are in milliseconds. Platform default clocks; 3 warmups, 15 samples and 1 GiB cache eviction. Only cache records with complete successful correctness and guard receipts are included. The most recent eligible measurement per baseline / case is shown.

[Download measurements](baseline-cache.json).

**Measurement update**

- 2026-11-06: replaced the complete torch-eager baseline set with 2208 verified current workloads across 205 operators. Physical 32 AI Cores / 64 Vector Cores; must_keep_origin_dtype, HF32 disabled; v3 device timing, 3 warmups and 15 raw profiler windows.
- All 2208 archives and correctness/guard receipts were verified for publication. Other libraries retain their recorded measurements and v2/v3 protocol labels.
- Reported times measure device work, excluding CPU input and parameter preparation. Independent reference routes and adaptations are retained in the campaign evidence.

**205 operators · 2208 / 2208 workloads with a baseline · 7758 baseline measurements.**

**Verified TileOPs results: 124 operators · 923 workloads.**

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
| torch-eager | 2208 |
| vllm-ascend | 793 |

## Data

| Page | Operators | Workloads | Baseline measurements |
| --- | ---: | ---: | ---: |
| [Elementwise](elementwise.md) | 70 | 527 | 1937 |
| [RoPE](rope.md) | 5 | 23 | 78 |
| [Reduction](reduction.md) | 19 | 176 | 668 |
| [Normalization](normalization.md) | 12 | 131 | 568 |
| [Conv & Pool](conv-pool.md) | 16 | 120 | 713 |
| [GEMM](gemm.md) | 8 | 235 | 818 |
| [Quantization & Dequantization](quantization.md) | 10 | 71 | 193 |
| [Attention](attention.md) | 20 | 256 | 775 |
| [MoE](moe.md) | 12 | 147 | 311 |
| [Sampling](sampling.md) | 6 | 48 | 59 |
| [Linear Attention](linear-attention.md) | 10 | 386 | 1506 |
| [SSM](ssm.md) | 10 | 54 | 81 |
| [Other](other.md) | 7 | 34 | 51 |
