@echo off
cd /d C:\Users\levi.lucena\Documents\Projetos\salux-ai-backend
set OPENAI_API_KEY=sk-...  @REM replace with your actual key
set OPENAI_MODEL=gpt-4o
C:\Users\levi.lucena\AppData\Local\Microsoft\WindowsApps\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000
pause
