# BanglaThon Ultimate 1-Click Windows Installer & Fixer
# Usage: irm https://raw.githubusercontent.com/tasfiqueofficial/BanglaThon/main/install.ps1 | iex

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   বাংলথন (BanglaThon) — উইন্ডোজ স্বয়ংক্রিয় ইনস্টলার ও ফিক্সার   " -ForegroundColor Cyan
Write-Host "   বাংলা ভাষার নিজস্ব প্রোগ্রামিং ল্যাঙ্গুয়েজ ও ইন্টারপ্রেটার   " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""

# 1. Check for Python or Py launcher
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command py -ErrorAction SilentlyContinue
}

if (-not $pythonCmd) {
    Write-Host "[!] কোনো পাইথন পাওয়া যায়নি। স্বয়ংক্রিয়ভাবে উইন্ডোজ প্যাকেজ ম্যানেজার (winget) দিয়ে পাইথন ইনস্টল করা হচ্ছে..." -ForegroundColor Yellow
    $wingetCmd = Get-Command winget -ErrorAction SilentlyContinue
    if ($wingetCmd) {
        winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    }
}

if ($pythonCmd) {
    $pyExe = $pythonCmd.Source
    $pyDir = Split-Path $pyExe
    Write-Host "[+] পাইথন পাওয়া গেছে: $pyExe" -ForegroundColor Green
    
    Write-Host "[+] BanglaThon ডাউনলোড ও আপডেট করা হচ্ছে..." -ForegroundColor Cyan
    & $pyExe -m pip install --upgrade git+https://github.com/tasfiqueofficial/BanglaThon.git --quiet
    
    # Get Python Scripts directory
    $scriptsDir = (& $pyExe -c "import sysconfig; print(sysconfig.get_path('scripts'))" 2>$null)
    if ($scriptsDir) { $scriptsDir = $scriptsDir.Trim() }

    # Prepare universal wrapper content
    $cmdContent = "@echo off`r`nwhere python >nul 2>nul`r`nif %ERRORLEVEL% equ 0 (`r`n    python -m bangla_lang %*`r`n) else (`r`n    py -m bangla_lang %*`r`n)"
    $ps1Content = "param([Parameter(ValueFromRemainingArguments=`$true)]`$p)`r`n& python -m bangla_lang @p"

    # Target folders to inject bangla executable into (covers ALL cases):
    $targetDirs = @()
    
    # Location 1: WindowsApps (Guaranteed to be in PATH on 100% of Windows 10/11)
    if ($env:LOCALAPPDATA -and (Test-Path "$env:LOCALAPPDATA\Microsoft\WindowsApps")) {
        $targetDirs += "$env:LOCALAPPDATA\Microsoft\WindowsApps"
    }
    
    # Location 2: Right next to python.exe (Guaranteed to be in PATH because python is active)
    if ($pyDir -and (Test-Path $pyDir)) {
        $targetDirs += $pyDir
    }
    
    # Location 3: Python Scripts directory
    if ($scriptsDir -and (Test-Path $scriptsDir)) {
        $targetDirs += $scriptsDir
    }
    
    # Location 4: User .bangla\bin
    $banglaHome = "$HOME\.bangla\bin"
    New-Item -ItemType Directory -Force -Path $banglaHome | Out-Null
    $targetDirs += $banglaHome

    # Write bangla.cmd and bangla.ps1 to all locations
    foreach ($dir in $targetDirs) {
        try {
            Set-Content -Path "$dir\bangla.cmd" -Value $cmdContent -Force -ErrorAction SilentlyContinue
            Set-Content -Path "$dir\bangla.bat" -Value $cmdContent -Force -ErrorAction SilentlyContinue
            Set-Content -Path "$dir\bangla.ps1" -Value $ps1Content -Force -ErrorAction SilentlyContinue
        } catch {}
    }

    # Ensure $banglaHome and $scriptsDir are in Windows User PATH permanently
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $newPaths = @($banglaHome)
    if ($scriptsDir) { $newPaths += $scriptsDir }

    foreach ($p in $newPaths) {
        if ($userPath -notlike "*$p*") {
            $userPath = "$userPath;$p"
        }
    }
    [Environment]::SetEnvironmentVariable("Path", $userPath, "User")

    # Update CURRENT active session PATH immediately so it works in the same window!
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + $userPath + ";$($targetDirs -join ';')"

    Write-Host ""
    Write-Host "==========================================================" -ForegroundColor Green
    Write-Host " [✓] অভিনন্দন! BanglaThon সম্পূর্ণ সফলভাবে প্রস্তুত হয়েছে!    " -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "এখনই যেকোনো ফোল্ডারে টার্মিনাল/CMD/VS Code-এ সরাসরি চালান:" -ForegroundColor Yellow
    Write-Host "   bangla run apnar_file.bl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "অথবা সরাসরি লাইভ কনসোলে লিখুন:" -ForegroundColor Yellow
    Write-Host "   bangla" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "[!] কম্পিউটারে পাইথন পাওয়া যায়নি। দয়া করে python.org থেকে Python ইনস্টল করে নিন।" -ForegroundColor Red
}
