"""
🪟 小问悬浮窗 - 一键配置工具
============================
自动检测环境、配置 CoPaw 定时任务、启动悬浮窗。
"""

import subprocess
import sys
import os
import json
import shutil

FLOATER_DIR = os.path.dirname(os.path.abspath(__file__))
FLOATER_PY = os.path.join(FLOATER_DIR, "copaw_floater.py")
START_BAT = os.path.join(FLOATER_DIR, "start.bat")
MESSAGE_JSON = os.path.join(FLOATER_DIR, "message.json")


def print_step(step, text):
    print(f"\n[{step}/5] {text}")


def check_python():
    """检查 Python 和 tkinter"""
    try:
        import tkinter
        print("  ✅ Python + tkinter 正常")
        return True
    except ImportError:
        print("  ❌ tkinter 不可用，请安装 Python（需包含 tkinter）")
        return False


def check_copaw():
    """检查 CoPaw 是否安装"""
    if shutil.which("copaw"):
        print("  ✅ CoPaw 已安装")
        # 检查是否在运行
        try:
            r = subprocess.run(
                ["copaw", "cron", "list", "--agent-id", "default"],
                capture_output=True, text=True, timeout=10
            )
            if r.returncode == 0:
                print("  ✅ CoPaw 服务运行中")
                return True
            else:
                print("  ⚠️  CoPaw 已安装但服务未启动")
                print("     请先运行：copaw desktop 或在终端执行 copaw serve")
                return False
        except:
            print("  ⚠️  CoPaw 已安装，但无法连接服务")
            return False
    else:
        print("  ❌ 未检测到 CoPaw")
        return False


def list_sessions():
    """列出可用会话"""
    try:
        r = subprocess.run(
            ["copaw", "chats", "list", "--agent-id", "default"],
            capture_output=True, text=True, timeout=15
        )
        if r.returncode != 0:
            return None
        
        lines = r.stdout.strip().split("\n")
        sessions = []
        for line in lines:
            if '"session_id"' in line:
                import re
                m = re.search(r'"session_id":\s*"([^"]+)"', line)
                if m:
                    sessions.append(m.group(1))
        return sessions
    except:
        return None


def setup_cron():
    """配置定时任务"""
    print("  CoPaw 定时任务可以让小问每隔15分钟自动发消息给你。")
    print("  这需要你当前的聊天会话 ID。")
    ans = input("  要配置定时任务吗？(y/n): ").strip().lower()
    if ans != "y":
        print("  ⏭ 跳过")
        return

    # 尝试自动获取会话
    sessions = list_sessions()
    session_id = None
    if sessions and len(sessions) > 0:
        print(f"\n  检测到 {len(sessions)} 个历史会话：")
        for i, sid in enumerate(sessions[:5]):
            print(f"    {i+1}. {sid}")
        print(f"  （将使用最近的一个）")
        session_id = sessions[0]
        use_it = input(f"  使用会话 {session_id}？(y/n): ").strip().lower()
        if use_it != "y":
            session_id = input("  请手动输入会话 ID: ").strip()
    else:
        session_id = input("  请手动输入会话 ID（可从 CoPaw 聊天界面获取）: ").strip()

    if not session_id:
        print("  ⏭ 已跳过")
        return

    # 创建 cron 任务（使用当前 session，会有通知弹框）
    cron_text = '[小问陪伴] 请先获取当前时间，然后生成一段暖心的陪伴话语写入message.json文件，注意根据时间段提醒休息/喝水/看文献/吃饭/睡觉。'
    
    cmd = [
        "copaw", "cron", "create",
        "--agent-id", "default",
        "--type", "agent",
        "--name", "小问陪伴",
        "--cron", "*/15 * * * *",
        "--channel", "console",
        "--target-user", "default",
        "--target-session", session_id,
        "--text", cron_text
    ]
    
    print("  ⏳ 正在创建定时任务...")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if r.returncode == 0:
        print("  ✅ 定时任务创建成功！每15分钟小问会发一次消息")
        print("  ⚠️ 注意：会有消息通知弹框，属正常现象")
    else:
        print(f"  ❌ 创建失败：{r.stderr[:200]}")
        print("  请参考 README.md 手动配置")


def setup_autostart():
    """添加开机自启（Windows）"""
    if sys.platform != "win32":
        return
    
    ans = input("\n  要添加开机自启吗？(y/n): ").strip().lower()
    if ans != "y":
        print("  ⏭ 跳过")
        return
    
    import winreg
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "小问悬浮窗", 0, winreg.REG_SZ, START_BAT)
        winreg.CloseKey(key)
        print("  ✅ 开机自启已添加！下次开机自动启动")
    except Exception as e:
        print(f"  ❌ 添加失败：{e}")
        print("  可以手动把 start.bat 添加到开机启动项")


def start_floater():
    """启动悬浮窗"""
    print("\n  🚀 正在启动悬浮窗...")
    if sys.platform == "win32":
        subprocess.Popen(["start", "/min", "pythonw", FLOATER_PY], shell=True)
    else:
        subprocess.Popen(["python3", FLOATER_PY])
    print("  ✅ 悬浮窗已启动！")


def main():
    print("=" * 50)
    print("  🪟 小问悬浮窗 - 一键配置工具")
    print("=" * 50)

    # 1. 检查 Python
    print_step(1, "检查 Python 环境")
    if not check_python():
        sys.exit(1)

    # 2. 检查 CoPaw
    print_step(2, "检查 CoPaw")
    copaw_ok = check_copaw()

    # 3. 配置定时任务（仅当 CoPaw 可用时）
    print_step(3, "配置 CoPaw 定时任务（可选）")
    if copaw_ok:
        setup_cron()
    else:
        print("  ⏭ CoPaw 未安装或未运行，跳过定时任务配置")
        print("  你仍然可以直接编辑 message.json 显示自定义内容")

    # 4. 开机自启
    print_step(4, "开机自启（可选）")
    setup_autostart()

    # 5. 启动悬浮窗
    print_step(5, "启动悬浮窗")
    start_floater()

    print("\n" + "=" * 50)
    print("  🎉 配置完成！小问开始陪伴你~")
    print("=" * 50)
    print()
    print("  📖 详细说明请查看 README.md")
    print("  🐛 遇到问题请提交 Issue")


if __name__ == "__main__":
    main()
