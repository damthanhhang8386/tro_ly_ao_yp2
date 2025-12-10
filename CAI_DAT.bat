@echo off
title CAI DAT MOI TRUONG YP2
echo --- DANG CAI DAT MOI TRUONG CHO PHAN MEM ---
echo.
echo 1. Dang cap nhat pip...
py -m pip install --upgrade pip

echo.
echo 2. Dang cai dat Streamlit va Google AI...
:: Chi cai dung 2 thu vien can thiet, loai bo cac thu vien gay loi
py -m pip install streamlit google-generativeai

echo.
echo -----------------------------------------------------
echo   DA CAI DAT XONG! 
echo   Bay gio ban co the chay file START_APP.bat
echo -----------------------------------------------------
pause