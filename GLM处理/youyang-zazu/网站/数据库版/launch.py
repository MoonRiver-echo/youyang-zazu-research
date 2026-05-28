#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单启动器：先构建数据库，然后启动 Web 界面，并自动打开浏览器
"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PY = sys.executable

def main():
    # 1) 构建数据库
    print("阶段1/3: 构建数据库，请稍候...")
    subprocess.run([PY, str(SCRIPT_DIR / "build_database.py")], check=True, cwd=str(SCRIPT_DIR))
    print("数据库构建完成。")

    # 2) 启动 Web 界面
    print("阶段2/3: 启动 Web 界面...")
    proc = subprocess.Popen([PY, str(SCRIPT_DIR / "web_interface.py")], cwd=str(SCRIPT_DIR))
    time.sleep(1)  # 给服务器一点启动时间

    # 3) 打开浏览器
    url = "http://localhost:8888"
    try:
        webbrowser.open(url)
    except Exception:
        print("请在浏览器中打开地址：", url)

    # 保持主进程运行，监听中断
    print("按 Ctrl+C 退出服务器。")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("退出...")
        if proc:
            proc.terminate()

if __name__ == "__main__":
    main()
