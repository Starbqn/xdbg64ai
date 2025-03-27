@echo off
REM Windows build script for Memory Debugger
REM This script builds the application and packages it for distribution

echo === Memory Debugger Windows Build ===
echo Building application...

REM Ensure build directory exists
if not exist builds mkdir builds

REM Run the Python build script
python build.py

REM Create the release package
python create_release.py

REM Move the release to builds directory
if not exist builds mkdir builds
for %%f in (releases\*.zip) do (
    copy "%%f" builds\
)

echo.
echo === Build Summary ===
echo Executable: dist\MemoryDebugger.exe
for %%f in (builds\*.zip) do (
    echo Release package: %%f
    goto :continue
)
:continue

echo.
echo To test the application, run:
echo   dist\MemoryDebugger.exe

pause