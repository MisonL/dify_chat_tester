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

REM Use spec file from build directory (where it should be)
set SPEC_FILE=%SCRIPT_DIR%\dify_chat_tester.spec
if not exist "%SPEC_FILE%" (
    echo Error: Spec file not found at %SPEC_FILE%
    pause
    exit /b 1
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
    if not exist "%RELEASE_DIR%" (
        echo Creating release directory...
        cd /d "%PROJECT_DIR%"
        mkdir release_windows
    )
    
    REM Copy executable and necessary files
    echo Copying executable...
    copy "%PROJECT_DIR%\dist\dify_chat_tester.exe" "%RELEASE_DIR%\"
    echo Copying config template...
    copy "%PROJECT_DIR%\config.env.example" "%RELEASE_DIR%\"
    echo Copying Excel template...
    copy "%PROJECT_DIR%\dify_chat_tester_template.xlsx" "%RELEASE_DIR%\"
    if exist "%PROJECT_DIR%\README.md" (
        echo Copying README...
        copy "%PROJECT_DIR%\README.md" "%RELEASE_DIR%\"
    )
    if exist "%PROJECT_DIR%\用户使用指南.md" (
        echo Copying user guide...
        copy "%PROJECT_DIR%\用户使用指南.md" "%RELEASE_DIR%\"
    )
    
    REM Create startup script
    echo @echo off > "%RELEASE_DIR%\run.bat"
    echo cd /d "%%~dp0" >> "%RELEASE_DIR%\run.bat"
    echo dify_chat_tester.exe >> "%RELEASE_DIR%\run.bat"
    echo pause >> "%RELEASE_DIR%\run.bat"
    
    REM Create compressed package
    echo Creating compressed package...
    
    REM Get timestamp for filename (alternative method for systems without wmic)
    for /f "tokens=2 delims==" %%a in ('powershell -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "datestamp=%%a"
    
    cd /d "%PROJECT_DIR%"
    
    REM Create ZIP archive
    echo Creating ZIP archive...
    py "%SCRIPT_DIR%create_release_zip.py"
    
    echo.
    echo Usage instructions:
    echo 1. Extract dify_chat_tester_windows_*.zip
    echo 2. Copy config.env.example to config.env
    echo 3. Edit config.env to configure API information
    echo 4. Double-click dify_chat_tester.exe to start the program
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