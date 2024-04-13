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

DDPM 原文：https://arxiv.org/pdf/2006.11239.pdf

DDPM 代码：https://github.com/hojonathanho/diffusion

图源 李宏毅老师课程：https://speech.ee.ntu.edu.tw/~hylee/ml/2023-spring.php

Diffusion **Training**及**Sampling**过程如下所示：

<img src="/images/diffusion_overview_1.png" width="500">

Diffusion 整个过程其实就是加噪再去噪，我们模型的神经网络唯一需要预测的部分就是噪声。

Training
---

<img src="/images/diffusion_2.png" width="500">

这张图展示了Diffusion training过程的伪代码

- 首先从数据集中sample一张图片
- 从 0 -> T 均匀分布中sample一个t
- 从均值为0方差为I的高斯分布中sample一个噪声
- 对我们刚刚Sample的噪声和模型预测的噪声做一个MSELoss，进行梯度下降



