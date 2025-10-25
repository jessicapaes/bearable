# PowerShell script to run Pain Relief Map
# Usage: Right-click and "Run with PowerShell" or run in terminal

Set-Location -Path "C:\Users\jessp\OneDrive\Education\AI Tech Institute Course\Repositories\painreliefmap"

# Set environment variables (replace with your actual API key if needed)
$env:OPENAI_API_KEY = "YOUR_API_KEY_HERE"
$env:OPENAI_MODEL = "gpt-3.5-turbo"

Write-Host "Starting Pain Relief Map..." -ForegroundColor Green
Write-Host "Opening browser at http://localhost:8501" -ForegroundColor Cyan

# Run Streamlit
& "C:\Users\jessp\Anaconda3\Scripts\streamlit.exe" run app\app_v8_auth_claude.py

Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")



