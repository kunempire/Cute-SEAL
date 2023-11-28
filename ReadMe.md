**Cute-SEAL** 比较了不同开源库对于全同态加密的计算效率. 

## Origin

《数据安全与隐私保护》 (2023-1) 的作业二.

## Function

本次实验选择了`Microsoft SEAL`和`TenSEAL`两种开源库, 比较了`BFV`和`CKKS`两种全同态加密算法. 在同一开源库TenSEAL中, 比较了BFV和CKKS两种算法; 在不同开源库Microsoft SEAL和TenSEAL, 比较了BFV算法.

本次实验选取了 M = 5 张 64*64 的RGB图片加密存储于文件中, 共进行5轮测试. 每轮测试随机选取 M = 5 张图片, 计算加密效率和匹配效率, 最后计算平均加密效率和匹配效率.

对于匹配度的计算, 采用余弦相似度:

$ \text{Cosine Similarity}(A, B) = \frac{{A \cdot B}}{{\|A\| \cdot \|B\|}} $

实验的一般流程可参考*demo.ipynb*.

## Structure

本仓库的目录结构如下, 根目录主要是测试`TenSEAL`开源库, 目录 *MS-SEAL* 是测试`Microsoft SEAL`开源库, 里面也有详细的说明文档.

`TenSEAL`的基本使用参照其[官方仓库](https://github.com/OpenMined/TenSEAL)的tutorials文件夹.

```bash
.
├── data
│   ├── encrypted # encrypted image files (binary)
│   ├── original # original images
│   └── test # test images
├── demo.ipynb # demo of testing process with TenSEAL
├── log # testing logs
│   ├── test-tensorflow-BFV.log
│   ├── test-tensorflow-CKKS.log
│   └── test-torch.log
├── MS-SEAL # Microsoft SEAL test
├── ReadMe.md
├── test-tensorflow.py # implement with tensorflow
└── test-torch.py # gpu implement with torch
```

## Improvement

Here are also the problems and shorts exiting ~~but author doesn't want to solve~~:

1. **Faster GPU.** 需要更进一步实现GPU上的全同态加密计算.
2. **Deep understanding.** 对开源库代码和全同态加密需要有更深的理解.

## Reference

[Microsoft SEAL官方仓库](https://github.com/Microsoft/SEAL)

[TenSEAL官方仓库](https://github.com/OpenMined/TenSEAL)

[基于全同态加密的安全人脸识别系统](https://github.com/DevilLost/Secure-Face-Recognition-System-based-on-Fully-Homomorphic-Encryption)

