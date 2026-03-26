@echo off
cd /d "C:\Users\Admin\Desktop\municipal-helpdesk"
call venv\Scripts\activate.bat
python manage.py makemigrations
python manage.py migrate
echo Migrations completed!
pause
