@echo off
chcp 65001 >nul
rem ================================================================
rem  KEO THA file kich ban .txt vao file nay de tao giong doc.
rem  Doi giong: sua dong VOICE ben duoi.
rem    Vi du: af_heart, af_bella, bf_emma, am_michael, am_fenrir, bm_george
rem    Tron 2 giong: am_michael:50,am_fenrir:50
rem  Doi toc do: sua dong SPEED (1.0 = binh thuong, 0.9 = cham hon)
rem ================================================================
set VOICE=af_heart
set SPEED=0.95

if "%~1"=="" (
  echo Hay keo tha file kich ban .txt vao file tao_giong.bat
  pause
  exit /b
)
"%~dp0.venv\Scripts\python.exe" "%~dp0tts_voice.py" "%~1" --voice "%VOICE%" --speed %SPEED%
pause
