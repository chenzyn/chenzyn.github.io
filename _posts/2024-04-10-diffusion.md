---
title: 'DDPM'
date: 2024-04-11
permalink: /posts/2024/04/blog-post-2/
tags:
  - Diffusion
  - 手撕系列
  - DDPM
---


Overview
===

DDPM 原文：[arxiv](https://arxiv.org/pdf/2006.11239.pdf)

DDPM 代码：[github](https://github.com/hojonathanho/diffusion)

图源 李宏毅老师课程：[https://speech.ee.ntu.edu.tw/~hylee/ml/2023-spring.php](https://speech.ee.ntu.edu.tw/~hylee/ml/2023-spring.php)


Diffusion 是一种生成模型，作者受到非平衡热力学的启发设计出了这套模型。
Diffusion 的整个过程即**加噪再去噪**，以一张图片为例，我们先简述diffusion的**前向过程**：
- 给定一张图片，我们随机sample一个高斯噪声，按照一定的比例加到原有的图片中，得到一张加噪的图片
- 重复`T`步加噪的过程，直到图片变成一张噪声图

<img src="/images/diffusion_3.png" width="500">

***为什么要不断的加噪声呢？***
Diffusion Model通过这样一个扩散过程逐渐向样本中添加噪声，直至样本被完全破坏，模型通过学习其中每一步扩散过程的噪声大小，实现从被破坏的样本恢复到原有样本的过程，来实现原样本的重建或生成。

Diffusion 的**后向过程**：
- 首先我们从一个高斯分布中sample一个高斯噪声
- 对这个高斯噪声进行`T`步重复的去噪操作，即之前加噪的逆过程
- 从而得到一个模型的生成结果

<img src="/images/diffusion_4.png" width="500">

说白了，Diffusion Model的目的就是学习如何基于第t步的条件（$$x_t$$, $$t$$）生成 `t` 步的 噪声 $$\epsilon_t$$

Diffusion **Training**及**Sampling**过程如下所示：

<img src="/images/diffusion_overview_1.png" width="500">


Training
---

<img src="/images/diffusion_2.png" width="500">

这张图展示了Diffusion training过程的伪代码

- 首先从数据集中sample一张图片
- 从 0 -> T 均匀分布中sample一个t
- 从均值为0方差为I的高斯分布中sample一个噪声
- 对我们刚刚Sample的噪声和模型预测的噪声做一个MSELoss，进行梯度下降

这里可以看出整个Diffusion过程中，我们需要模型做预测的部分就只有**噪声预测**的部分.

另外一个需要注意的点是，训练过程我们不是从 t:0->T 这样的模式去循环加噪的，而是**直接从中sample一个
`t`时间步**，进行加噪操作（_sample次数足够多时效果可视为等同_）

### 那么问题来了，假设我sample到`t==5`步，我是否需要从`t==0`开始加噪声，循环`5`步得到$$x_5$$?

>答案是**不需要**的，虽然原理上扩散过程是从$$x_0$$开始经过t:0->t的扩散过程一步步扩散得到`t`步的扩散图$$x_t$$，但实际上通过合并扩散过程的公式我们可以发现，得到$$x_t$$并不需要循环一步步加噪，而是可以通过一步计算得到$$x_t$$. 
我们以 $$x_2$$ 为例， **单步的扩散公式为$$x_t = \sqrt{1-\beta_{t}}x_{t-1} + \sqrt{\beta_t}\epsilon$$其中$$\alpha_t = 1 - \beta_t$$**
那么有 
$$x_1 = \sqrt{1-\beta_{1}}x_{0} + \sqrt{\beta_1}\epsilon_0$$
$$x_2 = \sqrt{1-\beta_{2}}x_{1} + \sqrt{\beta_2}\epsilon_1 $$
合并可得 $$x_2 = \sqrt{1-\beta_{2}}\sqrt{1-\beta_{1}}x_{0} + \sqrt{1-(1-\beta_2)(1-\beta_1)}\epsilon $$ （_由于噪声来自同一个高斯分布，所以噪声项可以这样合并_）
<img src="/images/diffusion_6.png" width="500">
同理可得 $$x_t = \sqrt{1-\beta_1}...\sqrt{1-\beta_t}x_0 + \sqrt{1-(1-\beta_1)...(1-\beta_t)}\epsilon$$
这里我们设 $$\bar{\alpha_t} = \alpha_1 \alpha_2 \alpha_3 ... \alpha_t$$
可以得到最终式 $$x_t = \sqrt{\bar{\alpha_t}}x_0 + \sqrt{1-\bar{\alpha_t}}\epsilon$$
这个式子意味着我们可以通过给定的$$x_0$$(_原图_) 以及时间步$$t$$ 通过一步计算得到任意时间步的 $$x_t$$(_t步加噪图_).

Sampling
---

<img src="/images/diffusion_5.png" width="500">

