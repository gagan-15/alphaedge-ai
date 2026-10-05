@echo off
setlocal
cd /d "%~dp0"
rem Load local, gitignored runtime configuration without echoing credentials.
if exist ".env" (
  for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
    if not "%%A"=="" if not "%%A:~0,1"=="#" set "%%A=%%B"
  )
)
set "PYTHON=%~dp0venv\Scripts\python.exe"
if not exist "%PYTHON%" set "PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
  echo AlphaEdge Python environment was not found.
  pause
  exit /b 1
)
where node >nul 2>&1 || (echo Node.js was not found. & pause & exit /b 1)
rem Only a loopback listener is AlphaEdge. Another desktop app may use 8000
rem on a LAN adapter and must not prevent the local backend from starting.
netstat -ano | findstr "127.0.0.1:8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 start "AlphaEdge Backend" /min cmd /c ""%PYTHON%" -m uvicorn backend.api.app:app --host 127.0.0.1 --port 8000"
netstat -ano | findstr ":5173" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 start "AlphaEdge Frontend" /min cmd /c "cd /d "%~dp0frontend" && npm.cmd run dev -- --host 127.0.0.1"
for /l %%N in (1,1,30) do (
  powershell -NoProfile -Command "try { if ((Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health/ -TimeoutSec 1).StatusCode -eq 200) { exit 0 } } catch {} ; exit 1" >nul 2>&1
  if not errorlevel 1 goto ready
  timeout /t 1 /nobreak >nul
)
echo AlphaEdge backend did not become healthy. Check backend logs.
pause
exit /b 1
:ready
start "" "http://127.0.0.1:5173/dashboard"
echo AlphaEdge is running with existing READY Dhan data.
endlocal
