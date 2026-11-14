@echo off
title DompetVibe.ai - Smart Financial Health Platform
color 0b

echo ======================================================================
echo           DOMPETVIBE.AI - SISTEM ANALISIS KEUANGAN PERILAKU
echo ======================================================================
echo.
echo [1/3] Memeriksa instalasi Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan di komputer ini!
    echo Silakan unduh dan pasang Python 3.10 atau versi lebih baru dari:
    echo https://www.python.org/downloads/
    echo Pastikan centang "Add python.exe to PATH" saat menginstal.
    echo.
    pause
    exit /b 1
)

echo [2/3] Memeriksa dan memasang dependensi (requirements.txt)...
echo Mohon tunggu sebentar...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [INFO] Menjalankan instalasi dependensi:
    pip install -r requirements.txt
)

echo.
echo [3/3] Menjalankan server aplikasi DompetVibe.ai...
echo.
echo ======================================================================
echo Server berjalan di: http://127.0.0.1:5000
echo Membuka aplikasi di web browser Anda secara otomatis...
echo (Tekan tombol Ctrl + C di jendela ini untuk menghentikan server)
echo ======================================================================
echo.

start "" "http://127.0.0.1:5000"
python app.py

pause
