@echo off
echo >>diskpart.txt select vdisk file="%1"
echo >>diskpart.txt attach vdisk
echo >>diskpart.txt exit
diskpart /s %CD%\diskpart.txt
del /q /f diskpart.txt
