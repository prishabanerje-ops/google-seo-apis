# Google SEO APIs — Windows Setup Script
# Run from repo root: .\setup\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "Google SEO APIs — Setup" -ForegroundColor White
Write-Host "──────────────────────────────────────────"

# 1. Find Python 3.8+
$pythonCmd = $null
foreach ($cmd in @("python", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -ge 3 -and $minor -ge 8) {
                $pythonCmd = $cmd
                Write-Host "  Python $major.$minor found" -ForegroundColor Green
                break
            }
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Host "Error: Python 3.8+ not found." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/"
    exit 1
}

# 2. Create virtual environment
$repoDir = Split-Path -Parent $PSScriptRoot
$venvDir = Join-Path $repoDir "venv"

if (Test-Path $venvDir) {
    Write-Host "  Existing venv found — skipping creation"
} else {
    Write-Host "  Creating virtual environment..."
    & $pythonCmd -m venv $venvDir
    Write-Host "  Virtual environment created" -ForegroundColor Green
}

# 3. Install dependencies
Write-Host "  Installing dependencies (this may take a minute)..."
$pip = Join-Path $venvDir "Scripts\pip.exe"
& $pip install -r (Join-Path $repoDir "requirements.txt") -q --disable-pip-version-check
Write-Host "  Dependencies installed" -ForegroundColor Green

# 4. Check credentials
Write-Host ""
Write-Host "Checking credentials..."
$python = Join-Path $venvDir "Scripts\python.exe"
& $python (Join-Path $repoDir "scripts\auth.py") --check

# 5. Next steps
Write-Host ""
Write-Host "Setup complete!" -ForegroundColor White
Write-Host ""
Write-Host "To run PageSpeed Insights:"
Write-Host "  venv\Scripts\activate" -ForegroundColor Yellow
Write-Host "  python scripts\psi.py https://example.com" -ForegroundColor Yellow
Write-Host ""
Write-Host "To run Search Console:"
Write-Host "  python scripts\gsc.py --property sc-domain:example.com" -ForegroundColor Yellow
Write-Host ""
Write-Host "Need credentials? See docs\03-credentials.md"
