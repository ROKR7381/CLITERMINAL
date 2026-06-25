# install.ps1 (Windows PowerShell)
Write-Host ""
Write-Host "🚀 Installing myagent CLI..." -ForegroundColor Cyan
Write-Host "------------------------------"

# 1. Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "❌ Python not found. Please install Python 3.9+ first:" -ForegroundColor Red
    Write-Host "   https://www.python.org/downloads/"
    exit 1
}

# Check Python version
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python (\d+)\.(\d+)") {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 9)) {
        Write-Host "❌ Python 3.9+ required. Current version: $pythonVersion" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Python $pythonVersion detected" -ForegroundColor Green
}

# 2. Check pip
$pip = Get-Command pip -ErrorAction SilentlyContinue
if (-not $pip) {
    Write-Host "❌ pip not found. Installing..."
    python -m ensurepip --upgrade
}

# 3. Install myagent
Write-Host "📦 Installing myagent from GitHub..."
pip install --upgrade git+https://github.com/ROKR7381/CLITERMINAL.git

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Installation failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ myagent installed successfully!" -ForegroundColor Green
Write-Host ""

# 4. Check API key
$apiKey = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")
if (-not $apiKey) {
    Write-Host ""
    Write-Host "⚠️  OPENAI_API_KEY not set!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "👉 Get your OpenAI API key here:"
    Write-Host "   https://platform.openai.com/api-keys"
    Write-Host ""
    Write-Host "👉 Then run this in PowerShell:"
    Write-Host '   setx OPENAI_API_KEY "sk-your-key-here"'
    Write-Host ""
    Write-Host "👉 Close terminal and reopen, then run:"
    Write-Host "   myagent"
} else {
    Write-Host "✅ API key detected"
    Write-Host ""
    Write-Host "🎉 Run:"
    Write-Host "   myagent"
    Write-Host "   myagent tui"
    Write-Host "   myagent run 'hello'"
}
Write-Host ""