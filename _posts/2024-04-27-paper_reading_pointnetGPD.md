---
title: 'Paper Reading: PointNetGPD: Detecting Grasp Configurations from Points Sets'
date: 2024-04-27
permalink: /posts/2024/04/blog-post-8/
tags:
  - Paper Reading
---

**原文地址**: [arxiv](https://arxiv.org/pdf/1809.06267)

略读
---

先看摘要：
为了解决定位机器人抓取的问题，他们提出了一个端到端的抓取评估模型,PointNetGPD相对于此前的评估方法更加轻量化而且可以直接处理gripper内部的点云(_什么意思不清楚，下面继续看_),他们的抓取评估网络以未处理过的点云作为输入，即使在点云很稀疏的情况下依然可以捕捉到复杂的gripper和目标物体间接触区域的复杂的几何信息，他们还用YCB物体集生成了一个包括350K真实点云和抓取的大规模数据集用来训练他们的模型。他们分别在模拟环境中和真机环境下定量评估了他们模型的能力。

看paper总结的contribution：
- 他们提出基于**PointNet**的网络架构**直接对3D点云进行几何分析来验证抓取质量**，对比其他基于CNN的方法，他们的方法可以更好的利用深度图中的3D几何信息而不需要手动提取特征，并且还可以保证相对较小的参数量来得到更高的学习和推理效率。他们还发现即使在点云很稀疏的情况下PointNetGPD也能work的很好，这说明PointNetGPD有处理不太完美的传感器数据。
- 他们还建立了一个包含**350K真实点云和para-gripper抓取的大规模数据集**，其中提供的精细的抓取质量分数结合了force-closure和GWS分析（_这是啥不知道_），他们的实验表明他们的抓取模型通过这个抓取质量分数和抓取label能显著提高performance。

搂一眼方法：
#### 首先是对问题的定义

给定一个物体$$o$$，其有关于抓取的属性包括：物体与gripper间的摩擦系数$$\gamma \in R$$，物体的几何信息，物体的质量信息$$M_o$$，以及 6 DOF 的抓取pose $$W_o \in R^6$$. 

因此我们可以定义物体的状态为$$s_o = (W_o, M_o, \gamma )$$，把抓取在三维空间中的表示定义为$$g=(p, r) \in R^6$$，其中 $$p=(x, y, z) \in R^3, r=(r_x, r_y, r_z) \in R^3 $$分别表示gripper的位置和旋转方向.




再看结果：
他们在模拟环境和真机环境下都做了测试。

**模拟环境**：
选用的baseline是[GPD](https://arxiv.org/pdf/1706.09911)，