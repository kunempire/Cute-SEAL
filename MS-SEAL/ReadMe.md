这里是对`Microsoft SEAL`进行测试的内容. 

`TenSEAL`的基本使用参照其[官方仓库](https://github.com/Microsoft/SEAL)的*native/examples*文件夹. 比如其中的*1_bfv_basis.cpp*是bfv算法的基本使用, *2_encoders.cpp*是bfv对多维向量等更高级的操作.

由于cpp的环境配置比较复杂, 特在*env_set.md*中进行了较为详细的说明.

## Structure

本仓库的目录结构如下.

```bash
.
├── build # CMkake build folder
├── CMakeLists.txt # CMake to make cpp project
├── data
│   ├── encrypted
│   └── original
│       └── original.zip
├── env_set.md
├── log
│   └── BFV_int.log
├── ReadMe.md
├── test_BFV.cpp
└── test_BFV.hpp
```

## Reference

[Microsoft SEAL官方仓库](https://github.com/Microsoft/SEAL)

