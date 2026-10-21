# Benchmark snapshot fixtures

`fixtures/` and `golden/` contain synthetic regression data and expected renderer
output, not measurements from this fork's current hardware. The NVIDIA H200,
CUDA version/error and `sm90` strings exercise compatibility with the upstream
NVIDIA snapshot schema. `test_renderer.py` passes the same fixture hardware label
explicitly. Preserve these labels with their fixtures; relabeling them as Ascend
would neither test a port nor establish an Ascend measurement.

The current fork's nightly platform and method are documented in
[`docs/timing.md`](../docs/timing.md). The renderer's legacy `cuda` environment
key and missing-field policy remain schema compatibility behavior.

这些目录保存合成回归输入及预期输出，不是当前硬件实测。NVIDIA H200、CUDA 与
`sm90` 标签用于覆盖上游快照 schema；不能把测试里的型号改成 Ascend 来冒充移植或测量。
