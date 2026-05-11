@echo off
REM Run this once on the server to install Python packages
REM Open File Manager in GoDaddy cPanel > Terminal or SSH

echo Installing Python dependencies...
%SystemDrive%\Python310\python.exe -m pip install --upgrade pip
%SystemDrive%\Python310\python.exe -m pip install -r requirements.txt

echo.
echo Done! Dependencies installed.
echo Now make sure your .env file has the correct values.
pause
