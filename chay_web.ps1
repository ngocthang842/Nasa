Write-Host "======================================================================" -ForegroundColor Green
Write-Host "  Dang khoi dong Dashboard RotaNA (NASA Space Apps Challenge)..." -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Green

if (Test-Path "D:\apps\Python312\python.exe") {
    & "D:\apps\Python312\python.exe" -m streamlit run app.py
} else {
    streamlit run app.py
}
