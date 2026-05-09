# 🪟 小问悬浮窗 —CoPaw 桌面陪伴助手

> 🤖 一个始终浮在屏幕最前面的暖心小窗，配合CoPaw 定时任务，定时推送暖心提醒、AI 资讯、旅游推荐等等，推送内容可以自己定制。

---
<img width="1706" height="805" alt="Qwenpaw悬浮窗" src="https://github.com/user-attachments/assets/ede7d286-2dd7-4843-974b-eeb4b9de5ce0" />

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🪟 **始终置顶** | 悬浮在所有窗口之上，工作摸鱼两不误 |
| 👁️ **半透明** | 不遮挡视线，优雅融入桌面 |
| 🖱️ **自由拖拽** | 点住窗口任意位置拖动 |
| 📏 **自由调大小** | 拖拽窗口边缘，想多大就多大 |
| 🔄 **滚轮滚动** | 文字太长？滚轮一滚就能看完 |
| 🎯 **CoPaw 联动** | 配合 CoPaw cron 定时任务，小问自动推送消息 |
| 💬 **自定义消息** | 写入 `message.json`，显示你想看的内容 |
| 🚀 **轻量无依赖** | 纯 Python 原生 tkinter，Windows / macOS / Linux 都能跑 |

---

## 📦 文件说明

```
📁 copaw-floater/
├── copaw_floater.py       # 🪟 悬浮窗主程序
├── start.bat              # 🚀 Windows 一键启动脚本
├── setup.py               # 🛠️ 一键配置工具（推荐先运行这个）
├── message.json           # 📝 消息文件（修改这里，悬浮窗自动更新）
└── README.md              # 📖 使用说明
```

---

## 🚀 快速开始

### 环境要求

- **Python 3.6+**（tkinter 通常随 Python 一起安装）
- **CoPaw**：如需定时推送功能，请先安装 [CoPaw](https://github.com/agentscope-ai/QwenPaw)

### 🛠️ 一键配置（推荐）

```bash
python setup.py
```

跟着提示走，脚本会自动完成所有配置和启动 ✅

### 手动启动

如果只想显示自定义文字，不配合 CoPaw：

#### Windows
双击 `start.bat`，右下角出现小窗 ✨

#### macOS / Linux
```bash
python3 copaw_floater.py &
```

然后编辑 `message.json` 写入想显示的内容即可。

---

## ⚙️ 自定义配置

### 配色方案

打开 `copaw_floater.py`，在文件开头的「配色方案」区域修改颜色值：

```python
COLOR_BG        = "#2C3E50"   # 主背景
COLOR_TITLE_BG  = "#34495E"   # 标题栏背景
COLOR_MSG_FG    = "#ECF0F1"   # 消息文字颜色
COLOR_ONLINE    = "#2ECC71"   # 在线状态颜色
```

### 透明度

```python
self.window.attributes('-alpha', 0.88)  # 0.0 ~ 1.0，越小越透明
```

### 刷新频率

```python
REFRESH_MS = 5000  # 毫秒，5000 = 5秒检查一次新消息
```

---

## ❓ 常见问题

### Q: 双击没反应？
确保 Python 已正确安装并添加到系统 PATH 中。在命令行输入 `python --version` 验证。

### Q: 不想用 CoPaw，只想显示固定文字？
直接编辑 `message.json`，写入你想显示的内容即可，悬浮窗会自动更新。


---

## 📄 许可证

MIT License

---

## 🙌 贡献

欢迎提交 Issue 和 PR！如果你有更好的想法，欢迎一起让「小问」变得更贴心～
