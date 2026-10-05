@echo off
setlocal
cd /d "%~dp0"
rem Load local ignored configuration without echoing values.
if exist ".env" (
  for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
    if not "%%A"=="" if not "%%A:~0,1"=="#" set "%%A=%%B"
  )
)
set "PYTHON=%~dp0venv\Scripts\python.exe"
if not exist "%PYTHON%" set "PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
  echo AlphaEdge Python environment was not found.
  if /I not "%~1"=="/scheduled" pause
  exit /b 1
)
"%PYTHON%" -m scripts.run_dhan_incremental_update
set "RESULT=%ERRORLEVEL%"
if "%RESULT%"=="0" (
  echo AlphaEdge incremental Dhan update completed safely.
) else (
  echo AlphaEdge incremental Dhan update failed. Existing READY data was preserved.
)
if /I not "%~1"=="/scheduled" pause
exit /b %RESULT%
