# cannbot 独立实测对比

本轮重测，使用磁盘上的 cannbot 源码、我们的 TileLang 编译器；没有启动 cannbot agent。未写入默认 coverage 或既有 150 行 / 49 达标口径。

D032：设备 kernel 区间并集，每次计时前驱逐 384 MiB L2，ABBA 顺序。每个 case 五轮，每轮 30 次调用；表中 ratio 为五轮 cannbot/ours 的中位数，范围为五轮最小值至最大值。单独一侧的耗时也是五轮中位数，两列耗时之商不必等于 ratio 的中位数。

Conv2d 复用原 workload、输入生成器和容差；其原 bench1 入口仅测正确性，本页使用独立计时驱动。Conv2d 的 SOL 未核验。无 bias 参数等源码限制按原样拒绝，拒绝原因保存在悬浮提示与原始数据中。

N≥5: **13/13 ops** · eager **71/95 cases** · graph **71/95 cases**.

[Raw case statistics](r322-evidence/cannbot-case-statistics.json) · [Summary](r322-evidence/cannbot-summary.json)

## Conv2dFwdOp

<div class="datatable"><table><thead><tr><th>Workload</th><th>Dtype</th><th>Regime</th><th>N / 5</th><th>Ours µs</th><th>cannbot µs</th><th>cannbot / ours</th><th>Range</th></tr></thead><tbody>
<tr><td><code>bottleneck-expand-1x1</code></td><td>float16</td><td>eager</td><td>5/5</td><td>22.5</td><td>28.5</td><td>1.2667×</td><td>1.2444–1.2778</td></tr>
<tr><td><code>bottleneck-expand-1x1</code></td><td>float16</td><td>graph</td><td>5/5</td><td>35.25</td><td>35.5</td><td>1.0142×</td><td>1.0035–1.0216</td></tr>
<tr><td><code>bottleneck-expand-1x1-bias</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>bottleneck-expand-1x1-bias</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>bottleneck-reduce-1x1</code></td><td>float16</td><td>eager</td><td>5/5</td><td>33.625</td><td>28.75</td><td>0.85502×</td><td>0.85185–0.86245</td></tr>
<tr><td><code>bottleneck-reduce-1x1</code></td><td>float16</td><td>graph</td><td>5/5</td><td>39.75</td><td>39.625</td><td>0.99375×</td><td>0.98742–1.0063</td></tr>
<tr><td><code>bottleneck-reduce-1x1-bias</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>bottleneck-reduce-1x1-bias</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>classifier-1x1</code></td><td>float16</td><td>eager</td><td>5/5</td><td>28.125</td><td>76.125</td><td>2.6968×</td><td>2.303–2.7411</td></tr>
<tr><td><code>classifier-1x1</code></td><td>float16</td><td>graph</td><td>5/5</td><td>35</td><td>77.125</td><td>2.2036×</td><td>1.9968–2.2962</td></tr>
<tr><td><code>classifier-1x1-bias</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>classifier-1x1-bias</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>deeplabv3-aspp-3x3-rate12</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&#x27;cannbot: docs/reports/R298-data/cannbot-kernels/conv2d.py::build_conv2d_kernel((1, 2048, 32, 32), (256, 2048, 3, 3), torch.float16) refused: NotImplementedError: conv2d dilation=12 is not supported; this kernel implements dilation=1 only&#x27;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>deeplabv3-aspp-3x3-rate12</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&#x27;cannbot: docs/reports/R298-data/cannbot-kernels/conv2d.py::build_conv2d_kernel((1, 2048, 32, 32), (256, 2048, 3, 3), torch.float16) refused: NotImplementedError: conv2d dilation=12 is not supported; this kernel implements dilation=1 only&#x27;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>default-dense-cube-fp16</code></td><td>float16</td><td>eager</td><td>5/5</td><td>87.5</td><td>26</td><td>0.29714×</td><td>0.29429–0.32429</td></tr>
<tr><td><code>default-dense-cube-fp16</code></td><td>float16</td><td>graph</td><td>5/5</td><td>87.75</td><td>26.5</td><td>0.30199×</td><td>0.2963–0.34375</td></tr>
<tr><td><code>dense-cube-bf16</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>53.875</td><td>39.75</td><td>0.73782×</td><td>0.6814–0.84028</td></tr>
<tr><td><code>dense-cube-bf16</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>54</td><td>38.375</td><td>0.71065×</td><td>0.66667–0.83796</td></tr>
<tr><td><code>depthwise-direct-fp16</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&#x27;cannbot: docs/reports/R298-data/cannbot-kernels/conv2d.py::build_conv2d_kernel((1, 4, 8, 9), (4, 1, 3, 3), torch.float16) refused: NotImplementedError: conv2d groups=4 is not supported; this kernel implements groups=1 only&#x27;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>depthwise-direct-fp16</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&#x27;cannbot: docs/reports/R298-data/cannbot-kernels/conv2d.py::build_conv2d_kernel((1, 4, 8, 9), (4, 1, 3, 3), torch.float16) refused: NotImplementedError: conv2d groups=4 is not supported; this kernel implements groups=1 only&#x27;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>dilation-cube-fp16</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&#x27;cannbot: docs/reports/R298-data/cannbot-kernels/conv2d.py::build_conv2d_kernel((1, 16, 9, 10), (16, 16, 3, 3), torch.float16) refused: NotImplementedError: conv2d dilation=2 is not supported; this kernel implements dilation=1 only&#x27;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>dilation-cube-fp16</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&#x27;cannbot: docs/reports/R298-data/cannbot-kernels/conv2d.py::build_conv2d_kernel((1, 16, 9, 10), (16, 16, 3, 3), torch.float16) refused: NotImplementedError: conv2d dilation=2 is not supported; this kernel implements dilation=1 only&#x27;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>fp32-direct</code></td><td>float32</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: cannbot&#x27;s conv2d.py::build_conv2d_kernel declares support for (&#x27;float16&#x27;, &#x27;bfloat16&#x27;); float32 is not one of them&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>fp32-direct</code></td><td>float32</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: cannbot&#x27;s conv2d.py::build_conv2d_kernel declares support for (&#x27;float16&#x27;, &#x27;bfloat16&#x27;); float32 is not one of them&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>grouped-direct-fp16</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&#x27;cannbot: docs/reports/R298-data/cannbot-kernels/conv2d.py::build_conv2d_kernel((1, 8, 9, 10), (8, 2, 3, 3), torch.float16) refused: NotImplementedError: conv2d groups=4 is not supported; this kernel implements groups=1 only&#x27;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>grouped-direct-fp16</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&#x27;cannbot: docs/reports/R298-data/cannbot-kernels/conv2d.py::build_conv2d_kernel((1, 8, 9, 10), (8, 2, 3, 3), torch.float16) refused: NotImplementedError: conv2d groups=4 is not supported; this kernel implements groups=1 only&#x27;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>highres-3x3-s1</code></td><td>float16</td><td>eager</td><td>5/5</td><td>29079</td><td>3656.1</td><td>0.12573×</td><td>0.12567–0.12579</td></tr>
<tr><td><code>highres-3x3-s1</code></td><td>float16</td><td>graph</td><td>5/5</td><td>29085</td><td>3661.9</td><td>0.1259×</td><td>0.12577–0.12599</td></tr>
<tr><td><code>highres-3x3-s1-bias</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>highres-3x3-s1-bias</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>large-grid-depthwise-fp16</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&#x27;cannbot: docs/reports/R298-data/cannbot-kernels/conv2d.py::build_conv2d_kernel((16, 256, 56, 56), (256, 1, 1, 1), torch.float16) refused: NotImplementedError: conv2d groups=256 is not supported; this kernel implements groups=1 only&#x27;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>large-grid-depthwise-fp16</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&#x27;cannbot: docs/reports/R298-data/cannbot-kernels/conv2d.py::build_conv2d_kernel((16, 256, 56, 56), (256, 1, 1, 1), torch.float16) refused: NotImplementedError: conv2d groups=256 is not supported; this kernel implements groups=1 only&#x27;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>late-stage-1x1</code></td><td>float16</td><td>eager</td><td>5/5</td><td>12.5</td><td>20.75</td><td>1.66×</td><td>1.6–1.7292</td></tr>
<tr><td><code>late-stage-1x1</code></td><td>float16</td><td>graph</td><td>5/5</td><td>21.25</td><td>25.25</td><td>1.1792×</td><td>1.1647–1.2024</td></tr>
<tr><td><code>late-stage-1x1-bias</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>late-stage-1x1-bias</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>midres-5x5-s1</code></td><td>float16</td><td>eager</td><td>5/5</td><td>4193.6</td><td>794.62</td><td>0.18948×</td><td>0.18916–0.19091</td></tr>
<tr><td><code>midres-5x5-s1</code></td><td>float16</td><td>graph</td><td>5/5</td><td>4199.5</td><td>806.12</td><td>0.19185×</td><td>0.19154–0.1923</td></tr>
<tr><td><code>midres-5x5-s1-bias</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>midres-5x5-s1-bias</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>mobilenetv2-depthwise</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&#x27;cannbot: docs/reports/R298-data/cannbot-kernels/conv2d.py::build_conv2d_kernel((1, 32, 56, 56), (32, 1, 3, 3), torch.float16) refused: NotImplementedError: conv2d groups=32 is not supported; this kernel implements groups=1 only&#x27;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>mobilenetv2-depthwise</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&#x27;cannbot: docs/reports/R298-data/cannbot-kernels/conv2d.py::build_conv2d_kernel((1, 32, 56, 56), (32, 1, 3, 3), torch.float16) refused: NotImplementedError: conv2d groups=32 is not supported; this kernel implements groups=1 only&#x27;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>resnet-1x1</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>15.25</td><td>18.25</td><td>1.1967×</td><td>1.1774–1.2131</td></tr>
<tr><td><code>resnet-1x1</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>36.75</td><td>25.75</td><td>0.70068×</td><td>0.70068–0.70748</td></tr>
<tr><td><code>resnet-1x1</code></td><td>float16</td><td>eager</td><td>5/5</td><td>15.75</td><td>18.375</td><td>1.1746×</td><td>1.1429–1.184</td></tr>
<tr><td><code>resnet-1x1</code></td><td>float16</td><td>graph</td><td>5/5</td><td>37.75</td><td>25.875</td><td>0.68874×</td><td>0.68543–0.69</td></tr>
<tr><td><code>resnet-1x1-bias</code></td><td>bfloat16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>resnet-1x1-bias</code></td><td>bfloat16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>resnet-1x1-bias</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>resnet-1x1-bias</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>resnet-3x3</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>1198.2</td><td>398</td><td>0.33184×</td><td>0.33045–0.33455</td></tr>
<tr><td><code>resnet-3x3</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>1206</td><td>405.25</td><td>0.33648×</td><td>0.33392–0.33776</td></tr>
<tr><td><code>resnet-3x3</code></td><td>float16</td><td>eager</td><td>5/5</td><td>1198.9</td><td>398.5</td><td>0.33212×</td><td>0.33167–0.33337</td></tr>
<tr><td><code>resnet-3x3</code></td><td>float16</td><td>graph</td><td>5/5</td><td>1202.1</td><td>407.12</td><td>0.33881×</td><td>0.3368–0.33954</td></tr>
<tr><td><code>resnet-3x3-bias</code></td><td>bfloat16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>resnet-3x3-bias</code></td><td>bfloat16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>resnet-3x3-bias</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>resnet-3x3-bias</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>resnext-grouped-3x3</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&#x27;cannbot: docs/reports/R298-data/cannbot-kernels/conv2d.py::build_conv2d_kernel((1, 128, 28, 28), (256, 4, 3, 3), torch.float16) refused: NotImplementedError: conv2d groups=32 is not supported; this kernel implements groups=1 only&#x27;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>resnext-grouped-3x3</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&#x27;cannbot: docs/reports/R298-data/cannbot-kernels/conv2d.py::build_conv2d_kernel((1, 128, 28, 28), (256, 4, 3, 3), torch.float16) refused: NotImplementedError: conv2d groups=32 is not supported; this kernel implements groups=1 only&#x27;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>stage-transition-3x3-s2</code></td><td>float16</td><td>eager</td><td>5/5</td><td>8355.4</td><td>1514.9</td><td>0.18131×</td><td>0.1803–0.18339</td></tr>
<tr><td><code>stage-transition-3x3-s2</code></td><td>float16</td><td>graph</td><td>5/5</td><td>8365.8</td><td>1523.5</td><td>0.18211×</td><td>0.18187–0.18441</td></tr>
<tr><td><code>stage-transition-3x3-s2-bias</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>stage-transition-3x3-s2-bias</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>stage-transition-5x5-s2</code></td><td>float16</td><td>eager</td><td>5/5</td><td>24029</td><td>3927.2</td><td>0.16341×</td><td>0.16278–0.16401</td></tr>
<tr><td><code>stage-transition-5x5-s2</code></td><td>float16</td><td>graph</td><td>5/5</td><td>24036</td><td>3932.2</td><td>0.16359×</td><td>0.16295–0.16449</td></tr>
<tr><td><code>stage-transition-5x5-s2-bias</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>stage-transition-5x5-s2-bias</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>stem-3x3-s2</code></td><td>float16</td><td>eager</td><td>5/5</td><td>389.25</td><td>255.75</td><td>0.65598×</td><td>0.64067–0.66399</td></tr>
<tr><td><code>stem-3x3-s2</code></td><td>float16</td><td>graph</td><td>5/5</td><td>394.5</td><td>260.38</td><td>0.66043×</td><td>0.64227–0.66593</td></tr>
<tr><td><code>stem-3x3-s2-bias</code></td><td>float16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>stem-3x3-s2-bias</code></td><td>float16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>stride-padding-nondiv-cube-fp16</code></td><td>float16</td><td>eager</td><td>5/5</td><td>36.5</td><td>22</td><td>0.60274×</td><td>0.59589–0.66897</td></tr>
<tr><td><code>stride-padding-nondiv-cube-fp16</code></td><td>float16</td><td>graph</td><td>5/5</td><td>36.75</td><td>21.5</td><td>0.58503×</td><td>0.57823–0.65529</td></tr>
<tr><td><code>stride2</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>1811.8</td><td>362.12</td><td>0.19983×</td><td>0.19829–0.20208</td></tr>
<tr><td><code>stride2</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>1817</td><td>375</td><td>0.20618×</td><td>0.20516–0.20681</td></tr>
<tr><td><code>stride2-bias</code></td><td>bfloat16</td><td>eager</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>stride2-bias</code></td><td>bfloat16</td><td>graph</td><td>0/5</td><td colspan="4"><abbr title="RuntimeError: no admissible cannbot candidate: [&quot;cannbot: Conv2dFwdOp: 3 operands -- cannbot&#x27;s build_conv2d_kernel has no bias parameter, so a case that declares bias_shape is a different operator expression and is refused rather than compared without the bias&quot;]">— 未达发布线 / 拒绝</abbr></td></tr>
</tbody></table></div>

## CountNonzeroFwdOp

<div class="datatable"><table><thead><tr><th>Workload</th><th>Dtype</th><th>Regime</th><th>N / 5</th><th>Ours µs</th><th>cannbot µs</th><th>cannbot / ours</th><th>Range</th></tr></thead><tbody>
<tr><td><code>3d-multidim-reduce</code></td><td>float16</td><td>eager</td><td>5/5</td><td>114.75</td><td>10.75</td><td>0.094092×</td><td>0.092613–0.099352</td></tr>
<tr><td><code>3d-multidim-reduce</code></td><td>float16</td><td>graph</td><td>5/5</td><td>114.62</td><td>17.75</td><td>0.15536×</td><td>0.14642–0.15733</td></tr>
<tr><td><code>sparsity-hidden</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>93.875</td><td>29</td><td>0.30892×</td><td>0.30441–0.31565</td></tr>
<tr><td><code>sparsity-hidden</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>103.5</td><td>36.75</td><td>0.35663×</td><td>0.3382–0.36594</td></tr>
<tr><td><code>sparsity-hidden</code></td><td>float16</td><td>eager</td><td>5/5</td><td>93.5</td><td>28</td><td>0.29867×</td><td>0.29669–0.30831</td></tr>
<tr><td><code>sparsity-hidden</code></td><td>float16</td><td>graph</td><td>5/5</td><td>101.88</td><td>35.5</td><td>0.34847×</td><td>0.33661–0.35096</td></tr>
<tr><td><code>sparsity-seq</code></td><td>float16</td><td>eager</td><td>5/5</td><td>40.875</td><td>8.75</td><td>0.21407×</td><td>0.20732–0.21951</td></tr>
<tr><td><code>sparsity-seq</code></td><td>float16</td><td>graph</td><td>5/5</td><td>55.25</td><td>12.875</td><td>0.23333×</td><td>0.22624–0.24528</td></tr>
</tbody></table></div>

## EluFwdOp

<div class="datatable"><table><thead><tr><th>Workload</th><th>Dtype</th><th>Regime</th><th>N / 5</th><th>Ours µs</th><th>cannbot µs</th><th>cannbot / ours</th><th>Range</th></tr></thead><tbody>
<tr><td><code>mlp-hidden</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>36</td><td>29.25</td><td>0.82909×</td><td>0.80903–0.84722</td></tr>
<tr><td><code>mlp-hidden</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>43.75</td><td>36</td><td>0.81714×</td><td>0.7507–0.82286</td></tr>
<tr><td><code>mlp-hidden</code></td><td>float16</td><td>eager</td><td>5/5</td><td>35</td><td>29.25</td><td>0.83571×</td><td>0.81915–0.85357</td></tr>
<tr><td><code>mlp-hidden</code></td><td>float16</td><td>graph</td><td>5/5</td><td>43</td><td>34.75</td><td>0.81548×</td><td>0.7933–0.82759</td></tr>
<tr><td><code>mlp-hidden-wide</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>68.25</td><td>57</td><td>0.83212×</td><td>0.82051–0.83883</td></tr>
<tr><td><code>mlp-hidden-wide</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>78</td><td>62.125</td><td>0.79167×</td><td>0.77882–0.8013</td></tr>
<tr><td><code>mlp-hidden-wide</code></td><td>float16</td><td>eager</td><td>5/5</td><td>67.625</td><td>55.25</td><td>0.8209×</td><td>0.81331–0.83396</td></tr>
<tr><td><code>mlp-hidden-wide</code></td><td>float16</td><td>graph</td><td>5/5</td><td>76.125</td><td>61</td><td>0.80265×</td><td>0.79024–0.81773</td></tr>
</tbody></table></div>

## GeluFwdOp

<div class="datatable"><table><thead><tr><th>Workload</th><th>Dtype</th><th>Regime</th><th>N / 5</th><th>Ours µs</th><th>cannbot µs</th><th>cannbot / ours</th><th>Range</th></tr></thead><tbody>
<tr><td><code>llama-8b-ffn-decode</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>3.5</td><td>1.75</td><td>0.5×</td><td>0.5–0.57143</td></tr>
<tr><td><code>llama-8b-ffn-decode</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>3.5</td><td>3.75</td><td>1.0714×</td><td>1–1.1429</td></tr>
<tr><td><code>llama-8b-ffn-prefill</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>184</td><td>128.25</td><td>0.69565×</td><td>0.69512–0.69837</td></tr>
<tr><td><code>llama-8b-ffn-prefill</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>193.75</td><td>135.5</td><td>0.70305×</td><td>0.69231–0.71336</td></tr>
<tr><td><code>llama-8b-ffn-prefill</code></td><td>float16</td><td>eager</td><td>5/5</td><td>181.75</td><td>125.25</td><td>0.69003×</td><td>0.68913–0.69103</td></tr>
<tr><td><code>llama-8b-ffn-prefill</code></td><td>float16</td><td>graph</td><td>5/5</td><td>190.75</td><td>134.38</td><td>0.69855×</td><td>0.69709–0.70446</td></tr>
</tbody></table></div>

## GemmFwdOp

<div class="datatable"><table><thead><tr><th>Workload</th><th>Dtype</th><th>Regime</th><th>N / 5</th><th>Ours µs</th><th>cannbot µs</th><th>cannbot / ours</th><th>Range</th></tr></thead><tbody>
<tr><td><code>ds-v3-decode-down</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>57.75</td><td>61.5</td><td>1.0563×</td><td>1.0377–1.0742</td></tr>
<tr><td><code>ds-v3-decode-down</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>67.375</td><td>70.25</td><td>1.0427×</td><td>1.0337–1.0627</td></tr>
<tr><td><code>ds-v3-decode-gate-up</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>71.5</td><td>77.375</td><td>1.0684×</td><td>1.0612–1.1014</td></tr>
<tr><td><code>ds-v3-decode-gate-up</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>73.75</td><td>86.5</td><td>1.1611×</td><td>1.1508–1.2</td></tr>
<tr><td><code>ds-v3-prefill-attn-proj</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>807</td><td>795.25</td><td>0.98528×</td><td>0.98344–0.98914</td></tr>
<tr><td><code>ds-v3-prefill-attn-proj</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>816.5</td><td>804.62</td><td>0.98637×</td><td>0.982–0.98683</td></tr>
<tr><td><code>ds-v3-prefill-attn-proj</code></td><td>float16</td><td>eager</td><td>5/5</td><td>826.5</td><td>794.88</td><td>0.962×</td><td>0.96098–0.96531</td></tr>
<tr><td><code>ds-v3-prefill-attn-proj</code></td><td>float16</td><td>graph</td><td>5/5</td><td>835.5</td><td>804.12</td><td>0.96245×</td><td>0.96031–0.96711</td></tr>
<tr><td><code>ds-v3-prefill-down</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>474.12</td><td>396.5</td><td>0.83628×</td><td>0.8336–0.83823</td></tr>
<tr><td><code>ds-v3-prefill-down</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>483.88</td><td>404.12</td><td>0.83467×</td><td>0.83423–0.84105</td></tr>
<tr><td><code>ds-v3-prefill-gate-up</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>484.38</td><td>455.5</td><td>0.94142×</td><td>0.93918–0.94273</td></tr>
<tr><td><code>ds-v3-prefill-gate-up</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>493.5</td><td>464.62</td><td>0.94149×</td><td>0.93466–0.94634</td></tr>
<tr><td><code>k-dominant-7168x16384</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>4800.6</td><td>4452.4</td><td>0.92159×</td><td>0.89613–0.95624</td></tr>
<tr><td><code>k-dominant-7168x16384</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>4777.4</td><td>4445.5</td><td>0.92044×</td><td>0.91487–0.95147</td></tr>
<tr><td><code>mid-m16-attn</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>110</td><td>107</td><td>0.97228×</td><td>0.96916–0.99511</td></tr>
<tr><td><code>mid-m16-attn</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>116</td><td>114.12</td><td>0.98511×</td><td>0.98242–1.0235</td></tr>
<tr><td><code>mid-m32-attn</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>103.25</td><td>101.62</td><td>0.98529×</td><td>0.97039–0.99031</td></tr>
<tr><td><code>mid-m32-attn</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>108.88</td><td>110.25</td><td>1.0142×</td><td>1.0116–1.0195</td></tr>
<tr><td><code>mid-m64-down</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>54</td><td>52.25</td><td>0.96774×</td><td>0.95305–0.98113</td></tr>
<tr><td><code>mid-m64-down</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>63.5</td><td>60.75</td><td>0.95525×</td><td>0.94118–1.0122</td></tr>
<tr><td><code>mid-m96-gate-up</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>68.25</td><td>68.5</td><td>1.0037×</td><td>0.97731–1.0282</td></tr>
<tr><td><code>mid-m96-gate-up</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>77</td><td>77</td><td>0.9984×</td><td>0.97727–1.0201</td></tr>
<tr><td><code>square-1k-nn</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>19.5</td><td>27.25</td><td>1.3846×</td><td>1.3797–1.3974</td></tr>
<tr><td><code>square-1k-nn</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>28.75</td><td>37</td><td>1.2845×</td><td>1.2542–1.3028</td></tr>
<tr><td><code>square-1k-nn</code></td><td>float16</td><td>eager</td><td>5/5</td><td>19.75</td><td>27.5</td><td>1.3924×</td><td>1.3671–1.4103</td></tr>
<tr><td><code>square-1k-nn</code></td><td>float16</td><td>graph</td><td>5/5</td><td>29.5</td><td>36.75</td><td>1.2231×</td><td>1.2119–1.317</td></tr>
<tr><td><code>wide-n-24576</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>1244.6</td><td>1014.5</td><td>0.8148×</td><td>0.80534–0.81914</td></tr>
<tr><td><code>wide-n-24576</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>1253.5</td><td>1023.4</td><td>0.81681×</td><td>0.80676–0.8217</td></tr>
</tbody></table></div>

## HardsigmoidFwdOp

<div class="datatable"><table><thead><tr><th>Workload</th><th>Dtype</th><th>Regime</th><th>N / 5</th><th>Ours µs</th><th>cannbot µs</th><th>cannbot / ours</th><th>Range</th></tr></thead><tbody>
<tr><td><code>mbv3-se-gate</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>1.75</td><td>1.5</td><td>0.85714×</td><td>0.85714–0.85714</td></tr>
<tr><td><code>mbv3-se-gate</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>2</td><td>2.5</td><td>1.25×</td><td>1.25–1.25</td></tr>
<tr><td><code>mbv3-se-gate</code></td><td>float16</td><td>eager</td><td>5/5</td><td>1.75</td><td>1.5</td><td>0.78571×</td><td>0.75–0.85714</td></tr>
<tr><td><code>mbv3-se-gate</code></td><td>float16</td><td>graph</td><td>5/5</td><td>2</td><td>2.5</td><td>1.25×</td><td>1.25–1.375</td></tr>
<tr><td><code>mbv3-se-gate-deep</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>2.25</td><td>2</td><td>0.88889×</td><td>0.88889–0.94444</td></tr>
<tr><td><code>mbv3-se-gate-deep</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>2.75</td><td>2.75</td><td>1×</td><td>1–1.1429</td></tr>
<tr><td><code>mbv3-se-gate-deep</code></td><td>float16</td><td>eager</td><td>5/5</td><td>2.25</td><td>2</td><td>0.88889×</td><td>0.88889–0.88889</td></tr>
<tr><td><code>mbv3-se-gate-deep</code></td><td>float16</td><td>graph</td><td>5/5</td><td>2.625</td><td>2.75</td><td>1.0476×</td><td>1.0476–1.2</td></tr>
</tbody></table></div>

## HardswishFwdOp

<div class="datatable"><table><thead><tr><th>Workload</th><th>Dtype</th><th>Regime</th><th>N / 5</th><th>Ours µs</th><th>cannbot µs</th><th>cannbot / ours</th><th>Range</th></tr></thead><tbody>
<tr><td><code>mbv3-stage2</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>37.5</td><td>35</td><td>0.92715×</td><td>0.91892–0.94079</td></tr>
<tr><td><code>mbv3-stage2</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>45.75</td><td>40.75</td><td>0.90055×</td><td>0.84409–0.93646</td></tr>
<tr><td><code>mbv3-stage2</code></td><td>float16</td><td>eager</td><td>5/5</td><td>37.125</td><td>34.375</td><td>0.92833×</td><td>0.91892–0.93289</td></tr>
<tr><td><code>mbv3-stage2</code></td><td>float16</td><td>graph</td><td>5/5</td><td>44.5</td><td>39.5</td><td>0.8764×</td><td>0.84817–0.89205</td></tr>
<tr><td><code>mbv3-stage3</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>24.25</td><td>22.5</td><td>0.92784×</td><td>0.91005–0.95833</td></tr>
<tr><td><code>mbv3-stage3</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>32.75</td><td>27.5</td><td>0.83969×</td><td>0.81538–0.86992</td></tr>
<tr><td><code>mbv3-stage3</code></td><td>float16</td><td>eager</td><td>5/5</td><td>23.75</td><td>22.875</td><td>0.95812×</td><td>0.94737–0.97872</td></tr>
<tr><td><code>mbv3-stage3</code></td><td>float16</td><td>graph</td><td>5/5</td><td>31.5</td><td>27.5</td><td>0.89431×</td><td>0.87302–0.90299</td></tr>
</tbody></table></div>

## LeakyReluFwdOp

<div class="datatable"><table><thead><tr><th>Workload</th><th>Dtype</th><th>Regime</th><th>N / 5</th><th>Ours µs</th><th>cannbot µs</th><th>cannbot / ours</th><th>Range</th></tr></thead><tbody>
<tr><td><code>gan-feat</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>62.75</td><td>54.625</td><td>0.87052×</td><td>0.85827–0.87327</td></tr>
<tr><td><code>gan-feat</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>73.25</td><td>60.5</td><td>0.81229×</td><td>0.81208–0.91459</td></tr>
<tr><td><code>gan-feat</code></td><td>float16</td><td>eager</td><td>5/5</td><td>62.5</td><td>54.5</td><td>0.876×</td><td>0.86508–0.87903</td></tr>
<tr><td><code>gan-feat</code></td><td>float16</td><td>graph</td><td>5/5</td><td>73</td><td>60.75</td><td>0.84965×</td><td>0.81463–0.85274</td></tr>
<tr><td><code>gan-feat-deep</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>33</td><td>28.25</td><td>0.87109×</td><td>0.84496–0.87879</td></tr>
<tr><td><code>gan-feat-deep</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>42.25</td><td>34.75</td><td>0.82738×</td><td>0.81176–0.84302</td></tr>
<tr><td><code>gan-feat-deep</code></td><td>float16</td><td>eager</td><td>5/5</td><td>32</td><td>28.25</td><td>0.88281×</td><td>0.848–0.88462</td></tr>
<tr><td><code>gan-feat-deep</code></td><td>float16</td><td>graph</td><td>5/5</td><td>42.125</td><td>34</td><td>0.84472×</td><td>0.80712–0.86471</td></tr>
</tbody></table></div>

## MaskedFillFwdOp

<div class="datatable"><table><thead><tr><th>Workload</th><th>Dtype</th><th>Regime</th><th>N / 5</th><th>Ours µs</th><th>cannbot µs</th><th>cannbot / ours</th><th>Range</th></tr></thead><tbody>
<tr><td><code>elementwise-16M</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>75.5</td><td>75.25</td><td>0.99833×</td><td>0.99013–1.0099</td></tr>
<tr><td><code>elementwise-16M</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>80.5</td><td>80.75</td><td>1×</td><td>0.99048–1.0031</td></tr>
<tr><td><code>elementwise-16M</code></td><td>float16</td><td>eager</td><td>5/5</td><td>76.25</td><td>75.75</td><td>0.99494×</td><td>0.99007–1.013</td></tr>
<tr><td><code>elementwise-16M</code></td><td>float16</td><td>graph</td><td>5/5</td><td>80.5</td><td>80.5</td><td>1.0063×</td><td>0.99054–1.0262</td></tr>
<tr><td><code>elementwise-16M</code></td><td>float32</td><td>eager</td><td>5/5</td><td>129.62</td><td>129.5</td><td>1.0038×</td><td>0.99803–1.0086</td></tr>
<tr><td><code>elementwise-16M</code></td><td>float32</td><td>graph</td><td>5/5</td><td>136</td><td>136</td><td>1.0083×</td><td>0.97464–1.0303</td></tr>
<tr><td><code>elementwise-256M</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>1115.2</td><td>1166.6</td><td>1.0454×</td><td>1.0444–1.0492</td></tr>
<tr><td><code>elementwise-256M</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>1209.2</td><td>1179.5</td><td>0.9771×</td><td>0.97374–0.97975</td></tr>
<tr><td><code>elementwise-256M</code></td><td>float16</td><td>eager</td><td>5/5</td><td>1175.1</td><td>1135.2</td><td>0.9667×</td><td>0.96355–0.96778</td></tr>
<tr><td><code>elementwise-256M</code></td><td>float16</td><td>graph</td><td>5/5</td><td>1182</td><td>1140.8</td><td>0.96525×</td><td>0.96283–0.96604</td></tr>
</tbody></table></div>

## MishFwdOp

<div class="datatable"><table><thead><tr><th>Workload</th><th>Dtype</th><th>Regime</th><th>N / 5</th><th>Ours µs</th><th>cannbot µs</th><th>cannbot / ours</th><th>Range</th></tr></thead><tbody>
<tr><td><code>yolo-p3</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>189.75</td><td>87.25</td><td>0.45982×</td><td>0.44921–0.47303</td></tr>
<tr><td><code>yolo-p3</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>197.75</td><td>94.125</td><td>0.47398×</td><td>0.46617–0.48604</td></tr>
<tr><td><code>yolo-p3</code></td><td>float16</td><td>eager</td><td>5/5</td><td>187</td><td>88.25</td><td>0.47224×</td><td>0.45989–0.48131</td></tr>
<tr><td><code>yolo-p3</code></td><td>float16</td><td>graph</td><td>5/5</td><td>195.62</td><td>94.375</td><td>0.48051×</td><td>0.47519–0.50129</td></tr>
<tr><td><code>yolo-p4</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>96.75</td><td>46.25</td><td>0.4768×</td><td>0.46641–0.50515</td></tr>
<tr><td><code>yolo-p4</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>106</td><td>53.75</td><td>0.50708×</td><td>0.49406–0.52005</td></tr>
<tr><td><code>yolo-p4</code></td><td>float16</td><td>eager</td><td>5/5</td><td>95.5</td><td>47</td><td>0.49086×</td><td>0.47644–0.51436</td></tr>
<tr><td><code>yolo-p4</code></td><td>float16</td><td>graph</td><td>5/5</td><td>104.38</td><td>53.625</td><td>0.51377×</td><td>0.48588–0.5534</td></tr>
</tbody></table></div>

## ReluFwdOp

<div class="datatable"><table><thead><tr><th>Workload</th><th>Dtype</th><th>Regime</th><th>N / 5</th><th>Ours µs</th><th>cannbot µs</th><th>cannbot / ours</th><th>Range</th></tr></thead><tbody>
<tr><td><code>hidden-state-decode</code></td><td>bfloat16</td><td>eager</td><td>4/5</td><td colspan="4"><abbr title="device timing failed: RuntimeError: expected 1 kernel_details.csv under /home/dyq/workspace/docs/reports/R322-data/runs/pass-5/ReluFwdOp/profiler/ReluFwdOp_0006_case, got []">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>hidden-state-decode</code></td><td>bfloat16</td><td>graph</td><td>4/5</td><td colspan="4"><abbr title="device timing failed: RuntimeError: expected 1 kernel_details.csv under /home/dyq/workspace/docs/reports/R322-data/runs/pass-5/ReluFwdOp/profiler/ReluFwdOp_0006_case, got []">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>hidden-state-prefill</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>30.25</td><td>27.875</td><td>0.92917×</td><td>0.90496–0.94531</td></tr>
<tr><td><code>hidden-state-prefill</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>39.25</td><td>34.5</td><td>0.89634×</td><td>0.86624–0.94304</td></tr>
<tr><td><code>hidden-state-prefill</code></td><td>float16</td><td>eager</td><td>4/5</td><td colspan="4"><abbr title="D036 selection could not be measured (RuntimeError: expected 1 kernel_details.csv under /home/dyq/workspace/docs/reports/R322-data/runs/pass-4/ReluFwdOp/profiler/ReluFwdOp_0001_d036_ReluFwdOp_hidden-state-prefill_float16, got []); fell back to the pre-D036 first-match order, which this record says so that the number is not read as best-of-pool">— 未达发布线 / 拒绝</abbr></td></tr>
<tr><td><code>hidden-state-prefill</code></td><td>float16</td><td>graph</td><td>4/5</td><td colspan="4"><abbr title="graph fallback is not a cannbot comparison">— 未达发布线 / 拒绝</abbr></td></tr>
</tbody></table></div>

## SiluFwdOp

<div class="datatable"><table><thead><tr><th>Workload</th><th>Dtype</th><th>Regime</th><th>N / 5</th><th>Ours µs</th><th>cannbot µs</th><th>cannbot / ours</th><th>Range</th></tr></thead><tbody>
<tr><td><code>llama-8b-ffn-decode</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>2.5</td><td>1.75</td><td>0.7×</td><td>0.63636–0.7</td></tr>
<tr><td><code>llama-8b-ffn-decode</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>2.75</td><td>3.25</td><td>1.1818×</td><td>1.1818–1.3636</td></tr>
<tr><td><code>llama-8b-ffn-prefill</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>134.5</td><td>103.38</td><td>0.76514×</td><td>0.75235–0.79368</td></tr>
<tr><td><code>llama-8b-ffn-prefill</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>143.5</td><td>109.12</td><td>0.75259×</td><td>0.72903–0.78109</td></tr>
<tr><td><code>llama-8b-ffn-prefill</code></td><td>float16</td><td>eager</td><td>5/5</td><td>134.25</td><td>104.5</td><td>0.77623×</td><td>0.75282–0.79143</td></tr>
<tr><td><code>llama-8b-ffn-prefill</code></td><td>float16</td><td>graph</td><td>5/5</td><td>142.25</td><td>109.75</td><td>0.77153×</td><td>0.7551–0.77568</td></tr>
</tbody></table></div>

## SoftplusFwdOp

<div class="datatable"><table><thead><tr><th>Workload</th><th>Dtype</th><th>Regime</th><th>N / 5</th><th>Ours µs</th><th>cannbot µs</th><th>cannbot / ours</th><th>Range</th></tr></thead><tbody>
<tr><td><code>mlp-hidden</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>50.5</td><td>30.25</td><td>0.59901×</td><td>0.57711–0.6152</td></tr>
<tr><td><code>mlp-hidden</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>59.25</td><td>37.75</td><td>0.63713×</td><td>0.61588–0.64807</td></tr>
<tr><td><code>mlp-hidden</code></td><td>float16</td><td>eager</td><td>5/5</td><td>50</td><td>31.25</td><td>0.625×</td><td>0.60101–0.6393</td></tr>
<tr><td><code>mlp-hidden</code></td><td>float16</td><td>graph</td><td>5/5</td><td>58.625</td><td>38</td><td>0.65714×</td><td>0.6087–0.68696</td></tr>
<tr><td><code>mlp-hidden-wide</code></td><td>bfloat16</td><td>eager</td><td>5/5</td><td>98</td><td>58.5</td><td>0.60154×</td><td>0.59439–0.61675</td></tr>
<tr><td><code>mlp-hidden-wide</code></td><td>bfloat16</td><td>graph</td><td>5/5</td><td>106.75</td><td>65.75</td><td>0.61466×</td><td>0.6046–0.62191</td></tr>
<tr><td><code>mlp-hidden-wide</code></td><td>float16</td><td>eager</td><td>5/5</td><td>95.875</td><td>57.25</td><td>0.59713×</td><td>0.59192–0.62338</td></tr>
<tr><td><code>mlp-hidden-wide</code></td><td>float16</td><td>graph</td><td>5/5</td><td>105.5</td><td>64.5</td><td>0.61137×</td><td>0.6019–0.63765</td></tr>
</tbody></table></div>

