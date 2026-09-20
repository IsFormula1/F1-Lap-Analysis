# F1 Lap Analysis

基于 [FastF1](https://github.com/theOehrly/Fast-F1) 的 F1 单圈数据分析小工具，用于对比不同车手在同一场比赛中的圈速表现，并生成交互式可视化图表。

## 功能

- 加载指定赛季 / 分站 / 场次（练习赛、排位赛、正赛）的比赛数据，并自动本地缓存，避免重复下载
- 筛选任意车手的最快圈数据
- 计算两位车手最快圈之间的圈速差值（delta）
- 生成"速度-距离对比折线图 + Sector 时间对比表格"的交互式图表（基于 Plotly）
  - 折线图上会标出每个弯道的位置
  - 支持鼠标悬浮查看具体数值，支持缩放
  - 表格部分展示两位车手三个 Sector 的用时及差值

## 技术栈

- [FastF1](https://github.com/theOehrly/Fast-F1) —— 拉取 F1 官方圈速、遥测、赛程数据
- [pandas](https://pandas.pydata.org/) —— 数据处理（FastF1 底层数据结构基于 pandas）
- [Plotly](https://plotly.com/python/) —— 交互式图表

## 环境搭建

```bash
# 1. 创建并激活虚拟环境
python -m venv .venv
.venv\Scripts\Activate.ps1      # Windows PowerShell

# 2. 安装依赖
pip install -r requirements.txt
```

## 运行

```bash
python src/2024-MonacoGP-Q.py
```

首次运行会从 FastF1 官方数据源下载比赛数据并写入 `cache/` 文件夹，之后再次运行会优先读取本地缓存，速度更快。

## 项目结构

```
F1-Lap-Analysis/
├── src/
│   ├── 2024-MonacoGP-Q.py   # 主脚本：加载数据、筛选车手、计算 delta、调用画图
│   └── plotting.py          # 画图工具函数，封装了速度对比图 + Sector 表格的绘制逻辑
├── cache/                   # FastF1 数据缓存（已加入 .gitignore，不提交）
├── requirements.txt         # 项目依赖
├── PROGRESS.md              # 学习/开发过程记录
└── README.md
```

## 进度

本项目仍在持续开发中，会随着功能的完善不断更新本仓库。当前已实现的功能见上方"功能"部分，后续计划增加赛道图和带颜色的分段计时图，队友之间的颜色怎么区分，更多对比图，如油门，刹车，弯心速度，轮胎衰竭，进展策略等功能。

## 开发笔记

详细的学习过程和踩过的坑记录在 [PROGRESS.md](./PROGRESS.md)。