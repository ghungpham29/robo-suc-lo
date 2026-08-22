@echo off
chcp 65001 > nul
title ROBOT HUONG DAN VIEN TRIEN LAM VAN HOA - KALEPIC
echo ======================================================================
echo    🤖 ROBOT HƯỚNG DẪN VIÊN TRIỂN LÃM VĂN HÓA - KALEPIC (v5.2 PRO) 🤖
echo ======================================================================
echo.

cd /d "%~dp0"

REM 1. Ưu tiên môi trường ảo .venv của dự án
if exist "..\\.venv\\Scripts\\python.exe" (
    echo [*] Đang khởi chạy bằng môi trường ảo .venv...
    "..\\.venv\\Scripts\\python.exe" main.py
    goto end
)

if exist ".venv\\Scripts\\python.exe" (
    echo [*] Đang khởi chạy bằng môi trường ảo .venv...
    ".venv\\Scripts\\python.exe" main.py
    goto end
)

REM 2. Fallback sang lệnh python hệ thống
echo [*] Đang khởi chạy bằng Python hệ thống...
python main.py

:end
if errorlevel 1 (
    echo.
    echo [!] Đã có lỗi xảy ra trong quá trình chạy.
)
echo.
pause
