@echo off
cd /d "C:\Users\jessp\OneDrive\Education\AI Tech Institute Course\Repositories\painreliefmap"
set OPENAI_API_KEY=YOUR_API_KEY_HERE
set OPENAI_MODEL=gpt-3.5-turbo
C:\Users\jessp\Anaconda3\Scripts\streamlit.exe run app\app_v8_auth_claude.py
pause


