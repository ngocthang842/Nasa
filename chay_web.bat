@echo off
title RotaNA - He thong Ho tro Ra quyet dinh Luan canh Nong nghiep
echo ======================================================================
echo   Dang khoi dong Dashboard RotaNA (NASA Space Apps Challenge)...
echo ======================================================================
echo.

if exist "D:\apps\Python312\python.exe" (
    "D:\apps\Python312\python.exe" -m streamlit run app.py
) else (
    python -m streamlit run app.py
)

pause
