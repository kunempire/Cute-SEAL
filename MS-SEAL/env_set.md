## 前置软件

**Ubuntu**

```bash
sudo apt-get update
sudo apt-get install build-essential tar curl zip unzip
sudo apt-get cmake
gcc
```

**Windows**

Visual Studio或者类似于上面Ubuntu的配置.

## vcpkg

vcpkg是微软C++团队开发的适用于C和C++库的跨平台开源软件包管理器。它大大简化了Windows、Linux和macOS上第三方库相关的下载和配置操作，目前已有超过1600个第三方库可以通过vcpkg来安装。

Winodws和Ubuntu安装类似，可以参考[vcpkg官方仓库](https://github.com/Microsoft/vcpkg)

```bash
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
./bootstrap-vcpkg.sh  # ./bootstrap-vcpkg.bat for Windows
./vcpkg integrate install
./vcpkg install seal # 此处的[seal]可以替换为任意包名
```

如果用vcpkg安装包失败, 注意查看失败信息中是否含有缺少的依赖, 如果有下载即可.

## 集成开发环境IDE

### vscode

#### 插件

**必备**

- C/C++

- CMake

- CMake Tools

*添彩*

- Better C++ Syntax: 更好的语法着色，需要配合主题使用

- Clang-Format: 代码格式化工具

#### 工具链文件路径设置

Visual Studio Code 中的 CMake Tools

1. 工作区`settings.json`编辑

将以下内容添加到您的工作区的`settings.json`中将使 CMake Tools 自动使用 vcpkg 中的第三方库:
```json
{
  "cmake.configureSettings": {
    "CMAKE_TOOLCHAIN_FILE": "[vcpkg root]/scripts/buildsystems/vcpkg.cmake"
  }
}
```
或者

```json
"cmake.configureSettings": {
    "CMAKE_TOOLCHAIN_FILE": "[vcpkg root]/scripts/buildsystems/vcpkg.cmake",
    "VCPKG_TARGET_TRIPLET": "x64-windows"
}
```

2. CMake Tools 插件设置

在插件设置中搜索： cmake configure args

#### CMake

选择编译器和对应的CMakeLists.txt即可构建项目, vscode左侧可设置, 下侧可点击调试或运行.

CMakeLists.txt是一个用于CMake构建系统的配置文件. 它描述了如何构建一个项目，包括源代码文件、库和可执行文件的编译选项、链接选项等.

### Visual Studio

[Visual Studio开源库集成器Vcpkg全教程](https://blog.csdn.net/cjmqas/article/details/79282847)
