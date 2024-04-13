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

这里可以看出整个Diffusion过程中，我们需要模型做预测的部分就只有**噪声预测**的部分，

