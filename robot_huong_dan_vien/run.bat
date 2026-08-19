@echo off
chcp 65001 > nul
echo ======================================================================
echo    ROBOT HUONG DAN VIEN TRIEN LAM VAN HOA (PHIEN BAN v5.0 PRO)
echo ======================================================================
py -3.11 main.py
if errorlevel 1 (
    echo.
    echo [THONG BAO] Dang thu chay bang duong dan Python 3.11 truc tiep...
    "C:\Users\ADMIN\AppData\Local\Programs\Python\Python311\python.exe" main.py
)
pause
