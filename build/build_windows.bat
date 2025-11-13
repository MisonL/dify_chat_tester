@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo Windows Build Script
echo ==========================================

REM Get script directory
set SCRIPT_DIR=%~dp0
REM Get project root directory
set PROJECT_DIR=%SCRIPT_DIR%..

REM Switch to project root directory
cd /d "%PROJECT_DIR%"

echo Project directory: %PROJECT_DIR%
echo Build directory: %SCRIPT_DIR%
echo ==========================================

REM Check if py launcher is available
where py >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python py launcher not found
    echo Please install Python first
    pause
    exit /b 1
)

REM Check if uv is installed
py -m uv --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: uv not installed
    echo Installing uv...
    py -m pip install uv
)

REM Check Python version
echo Checking Python version...
py -m uv run python --version

REM Install/update dependencies
echo Installing/updating dependencies...
py -m uv sync

REM Install PyInstaller
echo Installing PyInstaller...
py -m uv add --dev pyinstaller

REM Clean previous build
echo Cleaning previous build...
if exist "%PROJECT_DIR%\dist\" (
    rmdir /s /q "%PROJECT_DIR%\dist\" 2>nul
)
if exist "%PROJECT_DIR%\build\dify_chat_tester\" (
    rmdir /s /q "%PROJECT_DIR%\build\dify_chat_tester\" 2>nul
)
if exist "%PROJECT_DIR%\build\dify_chat_tester.dist\" (
    rmdir /s /q "%PROJECT_DIR%\build\dify_chat_tester.dist\" 2>nul
)
if exist "%PROJECT_DIR%\build\dify_chat_tester.build\" (
    rmdir /s /q "%PROJECT_DIR%\build\dify_chat_tester.build\" 2>nul
)

REM Use spec file from project root directory first
set SPEC_FILE=%PROJECT_DIR%\dify_chat_tester.spec
if not exist "%SPEC_FILE%" (
    set SPEC_FILE=%SCRIPT_DIR%\dify_chat_tester.spec
    if not exist "%SPEC_FILE%" (
        echo Error: Spec file not found
        pause
        exit /b 1
    )
)

echo Using spec file: %SPEC_FILE%

REM Run PyInstaller
echo Starting packaging...
py -m uv run pyinstaller "%SPEC_FILE%"

REM Check build result
if exist "%PROJECT_DIR%\dist\dify_chat_tester.exe" (
    echo.
    echo Build successful!
    echo Executable location: %PROJECT_DIR%\dist\dify_chat_tester.exe
    
    REM Create release package
    set RELEASE_DIR=%PROJECT_DIR%\release_windows
    if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"
    
    REM Copy executable and necessary files
    copy "%PROJECT_DIR%\dist\dify_chat_tester.exe" "%RELEASE_DIR%\" >nul
    copy "%PROJECT_DIR%\config.env.example" "%RELEASE_DIR%\" >nul
    copy "%PROJECT_DIR%\dify_chat_tester_template.xlsx" "%RELEASE_DIR%\" >nul
    if exist "%PROJECT_DIR%\README.md" copy "%PROJECT_DIR%\README.md" "%RELEASE_DIR%\" >nul
    
    REM Create startup script
    echo @echo off > "%RELEASE_DIR%\run.bat"
    echo cd /d "%%~dp0" >> "%RELEASE_DIR%\run.bat"
    echo dify_chat_tester.exe >> "%RELEASE_DIR%\run.bat"
    echo pause >> "%RELEASE_DIR%\run.bat"
    
    REM Create compressed package
    echo Creating compressed package...
    
    REM Get timestamp for filename
    for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
    set "YYYY=%dt:~0,4%"
    set "MM=%dt:~4,2%"
    set "DD=%dt:~6,2%"
    set "HH=%dt:~8,2%"
    set "Min=%dt:~10,2%"
    set "Sec=%dt:~12,2%"
    set "datestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"
    
    cd /d "%PROJECT_DIR%"
    
    REM Try to create TAR archive (built-in in Windows 10/11)
    echo Creating TAR archive...
    tar -c -f "dify_chat_tester_windows_%datestamp%.tar" -C release_windows .
    
    REM If Python is available, also create ZIP
    echo Creating ZIP archive...
    py "%SCRIPT_DIR%create_release_zip.py"
    
    echo.
    echo Usage instructions:
    echo 1. Extract dify_chat_tester_windows_*.zip
    echo 2. Copy config.env.example to config.env
    echo 3. Edit config.env to configure API information
    echo 4. Double-click run.bat to start the program
    echo.
    echo Packaging complete!
) else (
    echo.
    echo Build failed!
    echo Please check error messages and retry
    pause
    exit /b 1
)

pause