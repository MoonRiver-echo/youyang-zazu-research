@echo off
chcp 65001 >nul
echo ========================================
echo  《酉阳杂俎》数据库查询系统
echo ========================================
echo.
echo 正在启动服务器...
echo.
start python "C:\Users\lx\Desktop\前期准备\GLM处理\web_interface.py"
echo 服务器启动中，请稍候...
timeout /t 3 /nobreak >nul
echo.
echo 正在打开浏览器...
start http://localhost:8888
echo.
echo 如果浏览器没有自动打开，请手动访问: http://localhost:8888
echo.
pause
