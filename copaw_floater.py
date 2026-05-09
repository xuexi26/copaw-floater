"""
🤖 小问悬浮窗 - 桌面陪伴助手
============================
功能：始终显示在桌面最前面，展示小问的暖心消息
     支持拖拽移动、自由调整大小、半透明、右键菜单
     
运行方式：双击本文件 或 双击 start.bat
"""

import tkinter as tk
import json
import os
import sys
from datetime import datetime

# ============ 配置 ============
MESSAGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "message.json")
REFRESH_MS = 5000  # 每5秒检查一次新消息

# 配色方案 - 清爽简洁风
COLOR_BG        = "#2C3E50"   # 主背景 - 深蓝灰
COLOR_TITLE_BG  = "#34495E"   # 标题栏背景
COLOR_TITLE_FG  = "#ECF0F1"   # 标题文字
COLOR_MSG_FG    = "#ECF0F1"   # 消息文字
COLOR_TIME_FG   = "#7F8C8D"   # 时间文字
COLOR_ONLINE    = "#2ECC71"   # 在线绿色
COLOR_NEW_MSG   = "#3498DB"   # 新消息蓝色
COLOR_BORDER    = "#34495E"   # 边框色

# =============================


class XiaowenFloater:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("小问陪伴")
        
        # ---- 窗口样式 ----
        self.MIN_W = 240
        self.MIN_H = 140
        self.W = 380
        self.H = 260
        self.RESIZE_MARGIN = 6  # 边缘检测宽度
        
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        
        # 默认位置：右下角（避开任务栏）
        pad_x, pad_y = 20, 70
        self.default_x = screen_w - self.W - pad_x
        self.default_y = screen_h - self.H - pad_y
        
        self.window.geometry(f"{self.W}x{self.H}+{self.default_x}+{self.default_y}")
        self.window.overrideredirect(True)          # 无边框
        self.window.attributes('-topmost', True)    # 始终置顶
        self.window.attributes('-alpha', 0.88)      # 半透明
        
        # ---- 交互状态 ----
        self.drag_start_x = None
        self.drag_start_y = None
        self.resize_mode = None   # None / 'right' / 'bottom' / 'corner'
        self.is_resizing = False  # 正在调整大小（区别于拖拽）
        self.resize_start_x = 0
        self.resize_start_y = 0
        self.resize_start_w = 0
        self.resize_start_h = 0
        
        # ---- 构建UI ----
        self._build_ui()
        
        # ---- 启动定时刷新 ----
        self._refresh_message()
        self._tick_clock()
        
        # ---- 绑定事件 ----
        # 鼠标移动（检测边缘）
        self.window.bind("<Motion>", self._on_mouse_move)
        # 鼠标按下（区分拖拽和调大小）
        self.window.bind("<Button-1>", self._on_mouse_down)
        # 鼠标拖动
        self.window.bind("<B1-Motion>", self._on_mouse_drag)
        # 鼠标释放
        self.window.bind("<ButtonRelease-1>", self._on_mouse_up)
        # 右键菜单
        self.window.bind("<Button-3>", self._on_right_click)
        # 递归绑定到所有子部件
        for child in self.window.winfo_children():
            self._bind_recursive(child, "<Motion>", self._on_mouse_move)
            self._bind_recursive(child, "<Button-1>", self._on_mouse_down)
            self._bind_recursive(child, "<B1-Motion>", self._on_mouse_drag)
            self._bind_recursive(child, "<ButtonRelease-1>", self._on_mouse_up)
            self._bind_recursive(child, "<Button-3>", self._on_right_click)

    def _bind_recursive(self, widget, event, callback):
        """递归绑定事件到所有子部件"""
        widget.bind(event, callback)
        for child in widget.winfo_children():
            self._bind_recursive(child, event, callback)

    def _build_ui(self):
        """构建界面"""
        # ---- 主体框架 ----
        self.frame = tk.Frame(
            self.window,
            bg=COLOR_BG,
            highlightbackground=COLOR_BORDER,
            highlightthickness=1,
            highlightcolor=COLOR_BORDER
        )
        self.frame.pack(fill=tk.BOTH, expand=True)

        # ---- 标题栏 ----
        title_bar = tk.Frame(self.frame, bg=COLOR_TITLE_BG, height=32)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        # 小问名字
        tk.Label(
            title_bar,
            text="小问",
            font=("Microsoft YaHei", 10, "bold"),
            bg=COLOR_TITLE_BG,
            fg=COLOR_TITLE_FG
        ).pack(side=tk.LEFT, padx=(12, 0), pady=0)

        # 状态指示器
        self.status_icon = tk.Label(
            title_bar,
            text="●",
            font=("Microsoft YaHei", 9),
            bg=COLOR_TITLE_BG,
            fg=COLOR_ONLINE
        )
        self.status_icon.pack(side=tk.RIGHT, padx=(0, 6), pady=0)

        self.status_text = tk.Label(
            title_bar,
            text="陪伴中",
            font=("Microsoft YaHei", 8),
            bg=COLOR_TITLE_BG,
            fg=COLOR_TIME_FG
        )
        self.status_text.pack(side=tk.RIGHT, padx=(0, 10), pady=0)

        # ---- 消息内容区（Text组件，支持滚轮滚动） ----
        msg_frame = tk.Frame(self.frame, bg=COLOR_BG)
        msg_frame.pack(fill=tk.BOTH, expand=True, padx=(14, 14), pady=(8, 6))

        self.msg_text = tk.Text(
            msg_frame,
            font=("Microsoft YaHei", 10),
            bg=COLOR_BG,
            fg=COLOR_MSG_FG,
            wrap=tk.WORD,           # 按单词自动换行
            relief=tk.FLAT,         # 无边框
            highlightthickness=0,
            borderwidth=0,
            padx=2,
            pady=2,
            state=tk.DISABLED       # 只读，禁止编辑
        )
        self.msg_text.pack(expand=True, fill=tk.BOTH)
        # 绑定滚轮事件
        self.msg_text.bind("<MouseWheel>", self._on_text_scroll)

        # ---- 底部栏 ----
        bottom_bar = tk.Frame(self.frame, bg=COLOR_BG, height=24)
        bottom_bar.pack(fill=tk.X)
        bottom_bar.pack_propagate(False)

        # 提示文字
        tk.Label(
            bottom_bar,
            text="拖拽移动 · 拉边调大小 · 右键菜单",
            font=("Microsoft YaHei", 7),
            bg=COLOR_BG,
            fg=COLOR_TIME_FG
        ).pack(side=tk.LEFT, padx=10)

        # 时间
        self.time_label = tk.Label(
            bottom_bar,
            text="",
            font=("Microsoft YaHei", 8),
            bg=COLOR_BG,
            fg=COLOR_TIME_FG
        )
        self.time_label.pack(side=tk.RIGHT, padx=10)

    # ========== 鼠标交互（拖拽 + 调整大小） ==========

    def _on_mouse_move(self, event):
        """检测鼠标位置，改变光标形状"""
        x, y = event.x, event.y
        w, h = self.W, self.H
        m = self.RESIZE_MARGIN

        on_right = (w - m <= x <= w)
        on_bottom = (h - m <= y <= h)
        on_corner = on_right and on_bottom

        if on_corner:
            self.window.config(cursor="bottom_right_corner")
            self.resize_mode = "corner"
        elif on_right:
            self.window.config(cursor="sb_h_double_arrow")
            self.resize_mode = "right"
        elif on_bottom:
            self.window.config(cursor="sb_v_double_arrow")
            self.resize_mode = "bottom"
        else:
            self.window.config(cursor="arrow")
            self.resize_mode = None

    def _on_mouse_down(self, event):
        """鼠标按下：边缘→开始调大小，内部→开始拖拽"""
        if self.resize_mode:
            # 在边缘 → 开始调整大小
            self.is_resizing = True
            self.resize_start_x = event.x_root
            self.resize_start_y = event.y_root
            self.resize_start_w = self.W
            self.resize_start_h = self.H
        else:
            # 在内部 → 开始拖拽
            self.is_resizing = False
            self.drag_start_x = event.x
            self.drag_start_y = event.y

    def _on_mouse_drag(self, event):
        """鼠标拖动：根据模式执行调整大小或拖拽"""
        if self.is_resizing:
            self._do_resize(event)
        elif self.drag_start_x is not None:
            self._do_drag(event)

    def _do_resize(self, event):
        """执行调整大小"""
        dx = event.x_root - self.resize_start_x
        dy = event.y_root - self.resize_start_y

        new_w = self.resize_start_w
        new_h = self.resize_start_h

        if self.resize_mode in ("right", "corner"):
            new_w = max(self.MIN_W, self.resize_start_w + dx)
        if self.resize_mode in ("bottom", "corner"):
            new_h = max(self.MIN_H, self.resize_start_h + dy)

        self.W = new_w
        self.H = new_h
        self.window.geometry(f"{new_w}x{new_h}")

    def _do_drag(self, event):
        """执行拖拽移动"""
        x = self.window.winfo_x() + event.x - self.drag_start_x
        y = self.window.winfo_y() + event.y - self.drag_start_y
        self.window.geometry(f"+{x}+{y}")

    def _on_mouse_up(self, event):
        """鼠标释放：重置所有状态"""
        self.is_resizing = False
        self.drag_start_x = None
        self.drag_start_y = None

    # ========== 消息刷新 ==========

    def _refresh_message(self):
        """读取 message.json 并更新显示"""
        try:
            if os.path.exists(MESSAGE_FILE):
                with open(MESSAGE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                msg = data.get("message", "").strip()
            else:
                msg = ""
            if not msg:
                msg = "🤖 小问陪伴已启动！\n\n配置消息源后，我会在这里显示暖心提醒～\n详见项目 README 或使用说明。"
            current = self.msg_text.get("1.0", "end-1c")
            if msg != current:
                self.msg_text.config(state=tk.NORMAL)
                self.msg_text.delete("1.0", tk.END)
                self.msg_text.insert("1.0", msg)
                self.msg_text.see("1.0")
                self.msg_text.config(state=tk.DISABLED)
                self._flash_status("💬 新消息", COLOR_NEW_MSG)
        except (json.JSONDecodeError, OSError):
            pass
        self.window.after(REFRESH_MS, self._refresh_message)

    def _on_text_scroll(self, event):
        """鼠标滚轮滚动文字内容"""
        self.msg_text.yview_scroll(-1 * (event.delta // 120), "units")

    def _flash_status(self, text, color):
        """状态闪烁提示"""
        self.status_text.config(text=text, fg=color)
        self.status_icon.config(fg=color)
        self.window.after(3000, lambda: (
            self.status_text.config(text="陪伴中", fg=COLOR_TIME_FG),
            self.status_icon.config(fg=COLOR_ONLINE)
        ))

    # ========== 时钟 ==========

    def _tick_clock(self):
        """更新底部时间"""
        now = datetime.now()
        self.time_label.config(text=now.strftime("%H:%M"))
        self.window.after(30000, self._tick_clock)

    # ========== 右键菜单 ==========

    def _on_right_click(self, event):
        menu = tk.Menu(self.window, tearoff=0,
                       bg=COLOR_TITLE_BG, fg=COLOR_TITLE_FG,
                       activebackground=COLOR_NEW_MSG,
                       activeforeground="white",
                       font=("Microsoft YaHei", 9))
        menu.add_command(
            label="📌 切换置顶",
            command=self._toggle_topmost
        )
        menu.add_command(
            label="📏 重置大小",
            command=self._reset_size
        )
        menu.add_separator()
        menu.add_command(
            label="🔁 回到右下角",
            command=self._reset_position
        )
        menu.add_separator()
        menu.add_command(
            label="❌ 退出",
            command=self._quit
        )
        menu.post(event.x_root, event.y_root)

    def _toggle_topmost(self):
        current = self.window.attributes("-topmost")
        self.window.attributes("-topmost", not current)
        status = "已置顶" if not current else "取消置顶"
        self._flash_status(f"📌 {status}", COLOR_NEW_MSG)

    def _reset_size(self):
        """恢复默认大小"""
        self.W = 380
        self.H = 260
        self.window.geometry(f"380x260")
        self._flash_status("📏 已重置大小", COLOR_NEW_MSG)

    def _reset_position(self):
        self.window.geometry(f"+{self.default_x}+{self.default_y}")
        self._flash_status("📍 回到原位", COLOR_NEW_MSG)

    def _quit(self):
        self.window.destroy()
        sys.exit(0)

    # ========== 启动 ==========

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = XiaowenFloater()
    app.run()
