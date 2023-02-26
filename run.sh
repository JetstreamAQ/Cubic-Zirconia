#!/bin/sh

clear
echo ================
echo Bot starting up.
echo ================

. bot-env/bin/activate

echo =======================================
echo Checking for updates for pip and yt-dlp
echo =======================================

pip3 install --upgrade pip

echo =======================================

pip3 install --upgrade yt-dlp

echo =======================================
echo Update/Check Complete...
echo =======================================

python3 main.py
