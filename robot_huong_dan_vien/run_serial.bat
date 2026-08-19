@echo off
chcp 65001 > nul
echo ======================================================================
echo    ROBOT HUONG DAN VIEN - CHE DO SERIAL DIEU KHIEN MATRIX MINI R4
echo ======================================================================
echo Dang khoi dong Serial Controller...
python serial_controller.py
if errorlevel 1 (
    echo.
    echo [THONG BAO] Dang thu chay bang duong dan Python 3.11 truc tiep...
    "C:\Users\ADMIN\AppData\Local\Programs\Python\Python311\python.exe" serial_controller.py
)
pause
