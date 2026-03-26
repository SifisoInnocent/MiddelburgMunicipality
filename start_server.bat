@echo off
cd /d "C:\Users\Admin\Desktop\municipal-helpdesk"
call venv\Scripts\activate.bat
python manage.py runserver 127.0.0.1:8000
