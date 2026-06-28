# 🚀 Win-NetSight: Windows 网络洞察者

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![C++](https://img.shields.io/badge/Language-C++17-blue.svg)](https://isocpp.org/)
[![Python](https://img.shields.io/badge/Language-Python3.12+-blue.svg)](https://www.python.org/)

**Win-NetSight** 是一款专注于 Windows 平台的高性能网络连接与流量监控工具。它利用 **C++** 直接调用 Windows 原生 API (IP Helper API, WinSock2) 进行底层数据采集，并通过 **Python** 优雅地在终端展示实时网络活动。

---

## ✨ 核心特性

- **🏎️ 原生高效**：C++ 采集核心直接使用 Windows IP Helper API，不依赖第三方驱动，轻量且高效。
- **🎨 实时洞察**：基于 Python `rich` 库构建，提供类似任务管理器的实时网络连接列表，包括协议、本地/远程地址、端口、PID 及连接状态。
- **📊 进程级监控**：能够关联网络连接到具体的进程 ID (PID)，帮助用户快速定位网络行为。
- **🧩 解耦架构**：C++ 后端负责数据采集，Python 前端负责数据展示，两者通过 JSON 管道通信，灵活且易于扩展。

## 🛠️ 工作原理

Win-NetSight 采用经典的客户端-服务器（这里是采集器-仪表盘）模型：
1. **核心采集器 (C++)**：一个独立的 Windows 可 executable 程序 (`netsight_core.exe`)，负责：
   - 初始化 Winsock。
   - 循环调用 `GetExtendedTcpTable` 和 `GetExtendedUdpTable` 等 IP Helper API，获取当前系统的 TCP 连接和 UDP 端口信息。
   - 将采集到的连接数据（协议、本地/远程 IP/端口、PID、状态等）格式化为 JSON 字符串，并通过标准输出 (stdout) 发送。
2. **终端仪表盘 (Python)**：负责：
   - 启动 C++ 采集器进程。
   - 实时读取 C++ 采集器通过管道输出的 JSON 数据流。
   - 解析 JSON 数据，并使用 `rich` 库在终端渲染出美观、实时的网络连接表格。

## 🚀 快速开始

### 环境要求
- **Windows**: Visual Studio (MSVC) 或 MinGW
- Python 3.12+

### 安装与运行

1. **克隆仓库**:
   ```bash
   git clone https://github.com/gggass/Win-NetSight.git
   cd Win-NetSight
   ```

2. **编译核心**:
   - **Windows (MSVC)**: `cl /EHsc /O2 netsight_core.cpp /link iphlpapi.lib ws2_32.lib /out:netsight_core.exe`
   - **Windows (MinGW)**: `g++ -O2 netsight_core.cpp -o netsight_core.exe -lws2_32 -liphlpapi`

3. **安装 Python 依赖**:
   ```bash
   pip install -r requirements.txt
   ```

4. **启动**:
   ```bash
   python win_netsight.py
   ```

## 📜 文件说明
- `netsight_core.cpp`: Windows 核心采集器源码 (C++)。
- `win_netsight.py`: 终端仪表盘脚本 (Python)。
- `Makefile`: Windows 编译脚本 (支持 MSVC 和 MinGW)。
- `requirements.txt`: Python 依赖库。

## 🤝 贡献指南
欢迎提交 Issue 或 Pull Request 来增加更多功能或优化 UI 体验。

## 📄 开源协议
本项目采用 MIT 协议开源。

---
由 **gggass** 精心打造。
