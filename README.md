# 皇室战争自动对战脚本

Python 自动对战脚本，用于皇室战争（Clash Royale）游戏自动化。

## 环境要求

- Python 3.8+
- Windows 系统
- 雷电模拟器（或安卓模拟器）

## 安装依赖

```bash
pip install pillow numpy pywin32
```

## 使用方法

1. 启动雷电模拟器
2. 运行脚本：

```bash
python main.py -m 10 -mode 1v1 -s aggressive -v
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| -m | 最大战斗场次 | 10 |
| -mode | 战斗模式 (1v1/2v2) | 1v1 |
| -s | 出牌策略 (aggressive/defensive/random) | aggressive |
| -v | 详细输出 | False |

## 策略说明

- **aggressive**: 激进策略，有圣水就出牌
- **defensive**: 防守策略，圣水够才出牌
- **random**: 随机策略

## 项目结构

```
cr_auto/
├── core/           # 核心模块
│   ├── controller.py
│   ├── detector.py
│   ├── device.py
│   └── screen.py
├── game/           # 游戏状态
├── tasks/          # 任务逻辑
├── utils/          # 工具函数
├── main.py         # 主入口
└── run.bat         # 快速启动脚本
```

## 注意事项

- 本脚本仅供学习交流使用
- 请遵守游戏服务条款
- 使用风险自担
