@echo off
setlocal enabledelayedexpansion

REM ==== CONFIGURATIONS ====
set "SOURCE=\\?\%USERPROFILE%\..\..\..\This PC\Afsana's S21\Internal storage\SHAREit\pictures\Camera"
set "DEST=F:\SAMSUNG S21\SHAREit\pictures\Camera"
set "CHUNK_SIZE=50"
set "SLEEP_TIME=1"

REM ==== CREATE DESTINATION IF NOT EXISTS ====
if not exist "%DEST%" (
    echo Creating destination folder...
    mkdir "%DEST%"
)

echo Copying files from:
echo %SOURCE%
echo to:
echo %DEST%
echo.

set /a count=0
for %%F in ("%SOURCE%\*.*") do (
    if not exist "%DEST%\%%~nxF" (
        echo Copying: %%~nxF
        copy "%%F" "%DEST%" >nul
        set /a count+=1

        if !count! geq %CHUNK_SIZE% (
            echo ================================
            echo Copied %CHUNK_SIZE% files. Pausing for %SLEEP_TIME% seconds...
            echo ================================
            timeout /t %SLEEP_TIME% >nul
            set /a count=0
        )
    )
)

echo.
echo ✅ All files copied successfully!
pause
