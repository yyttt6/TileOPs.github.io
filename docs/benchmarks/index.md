# Benchmarks

Baseline cache progress · Ascend 950DT · snapshot 2026-10-29T14:10:43+00:00

Latencies are measured baseline results. TileOPs timings are not included in this cache snapshot, so **Ratio = NaN** and TileOPs latency is **—**. This does not rate unfinished operators or claim performance acceptance.

Machines are displayed separately; results from different hosts or software cohorts are not used to calculate a speedup. Each baseline cell shows microseconds; `D` = profiler device latency, `H` = complete host round-trip latency. Platform default clocks; 3 warmups, 15 samples and 1 GiB cache eviction. Only cache records with complete successful correctness and guard receipts are included. The most recent valid record per host / baseline / case is shown.

[Download measurements and provenance](baseline-cache.json).

**168 operators · 1644 / 2062 workloads with a baseline · 4783 baseline measurements across 3 machines.**

Coverage is partial: a measured workload can still have other baselines pending. These are recorded results, not a claim that an operator is fully covered.

## Baseline coverage

| Baseline | Local | Server 1 | Server 2 | Total |
| --- | ---: | ---: | ---: | ---: |
| DeepGEMM-Ascend | 11 | 0 | 0 | 11 |
| DeepSelect | 30 | 0 | 0 | 30 |
| TileKernels | 98 | 0 | 0 | 98 |
| atvc | 0 | 0 | 43 | 43 |
| catlass | 0 | 0 | 247 | 247 |
| flash-linear-attention-npu | 376 | 77 | 0 | 453 |
| ops-fft | 0 | 0 | 2 | 2 |
| ops-math | 260 | 0 | 283 | 543 |
| ops-nn | 391 | 0 | 0 | 391 |
| ops-tensor | 0 | 0 | 69 | 69 |
| ops-transformer | 388 | 162 | 0 | 550 |
| sgl-kernel-npu | 305 | 462 | 62 | 829 |
| tilelang | 163 | 0 | 0 | 163 |
| tilelang-ascend | 9 | 49 | 503 | 561 |
| vllm-ascend | 1 | 17 | 775 | 793 |

## Data

| Page | Operators | Workloads | Baseline measurements |
| --- | ---: | ---: | ---: |
| [Elementwise](elementwise.md) | 64 | 450 | 1074 |
| [Reduction](reduction.md) | 19 | 169 | 384 |
| [Conv & Pool](conv-pool.md) | 16 | 117 | 525 |
| [Quantization & Dequantization](quantization.md) | 4 | 25 | 102 |
| [Attention](attention.md) | 15 | 174 | 509 |
| [MoE](moe.md) | 7 | 72 | 150 |
| [Sampling](sampling.md) | 3 | 11 | 11 |
| [Linear Attention](linear-attention.md) | 9 | 353 | 996 |
| [Other](other.md) | 31 | 273 | 1032 |
