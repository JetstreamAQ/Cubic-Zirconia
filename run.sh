#!/bin/sh

clear
echo ================
echo Bot starting up.
echo ================

. bot-env/bin/activate

echo =======================================
echo Checking for updates for pip and yt-dlp
echo =======================================

python3 -m pip install --upgrade pip

echo =======================================

python3 -m pip install --upgrade -r requirements.txt

echo =======================================
echo Update/Check Complete...
echo =======================================

python3 main.py
