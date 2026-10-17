@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3.12 -m venv .venv
  if errorlevel 1 goto :error
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :error
.venv\Scripts\python.exe setup.py
if errorlevel 1 goto :error
set OMP_NUM_THREADS=2
echo Mo trinh duyet tren may cua ban, cong 8787. Dung Ctrl+C de dung.
.venv\Scripts\python.exe -m uvicorn server:app --host 127.0.0.1 --port 8787
if errorlevel 1 goto :error
exit /b
:error
echo Khong khoi dong duoc. Hay chup lai thong bao loi phia tren.
pause
