# BanglaThon Ultimate 1-Click Windows Installer & Fixer
# Usage: irm https://raw.githubusercontent.com/tasfiqueofficial/BanglaThon/main/install.ps1 | iex

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   বাংলথন (BanglaThon) — উইন্ডোজ স্বয়ংক্রিয় ইনস্টলার ও ফিক্সার   " -ForegroundColor Cyan
Write-Host "   বাংলা ভাষার নিজস্ব প্রোগ্রামিং ল্যাঙ্গুয়েজ ও ইন্টারপ্রেটার   " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""

function Test-RealPython($cmd) {
    if (-not $cmd) { return $false }
    try {
        $out = & $cmd --version 2>&1 | Out-String
        if ($out -like "*Python 3*" -and $out -notlike "*not found*" -and $out -notlike "*MicrosoftStore*") {
            return $true
        }
    } catch {}
    return $false
}

$hasRealPy = $false
$realPyExe = ""

# Check 'py' launcher first
$pyLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($pyLauncher -and (Test-RealPython "py")) {
    $hasRealPy = $true
    $realPyExe = "py"
}

# Check 'python'
if (-not $hasRealPy) {
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd -and (Test-RealPython "python")) {
        $hasRealPy = $true
        $realPyExe = "python"
    }
}

# If no real Python, auto-install via winget
if (-not $hasRealPy) {
    Write-Host "[!] আপনার উইন্ডোজ ১১-তে আসল পাইথন পাওয়া যায়নি।" -ForegroundColor Yellow
    Write-Host "[+] উইন্ডোজ ১১ প্যাকেজ ম্যানেজার (winget) দিয়ে স্বয়ংক্রিয়ভাবে পাইথন ইনস্টল করা হচ্ছে..." -ForegroundColor Cyan
    
    $wingetCmd = Get-Command winget -ErrorAction SilentlyContinue
    if ($wingetCmd) {
        Write-Host "[+] পাইথন ডাউনলোড হচ্ছে, অনুগ্রহ করে ৩০-৪০ সেকেন্ড অপেক্ষা করুন..." -ForegroundColor White
        & winget install -e --id Python.Python.3.12 --scope user --override "/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1" --accept-package-agreements --accept-source-agreements
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        if (Test-RealPython "py") { $hasRealPy = $true; $realPyExe = "py" }
        elseif (Test-RealPython "python") { $hasRealPy = $true; $realPyExe = "python" }
    }
}

if ($hasRealPy) {
    Write-Host "[+] পাইথন সক্রিয় পাওয়া গেছে: $realPyExe" -ForegroundColor Green
    Write-Host "[+] BanglaThon ডাউনলোড ও ইনস্টল করা হচ্ছে..." -ForegroundColor Cyan
    
    & $realPyExe -m pip install --upgrade git+https://github.com/tasfiqueofficial/BanglaThon.git --quiet
    
    # Scripts directory
    $scriptsDir = (& $realPyExe -c "import sysconfig; print(sysconfig.get_path('scripts'))" 2>$null)
    if ($scriptsDir) { $scriptsDir = $scriptsDir.Trim() }

    # Universal Wrapper
    $cmdContent = "@echo off`r`nwhere py >nul 2>nul`r`nif %ERRORLEVEL% equ 0 (`r`n    py -m bangla_lang %*`r`n) else (`r`n    python -m bangla_lang %*`r`n)"
    $ps1Content = "param([Parameter(ValueFromRemainingArguments=`$true)]`$p)`r`nif (Get-Command py -ErrorAction SilentlyContinue) { & py -m bangla_lang @p } else { & python -m bangla_lang @p }"

    $targetDirs = @()
    if ($env:LOCALAPPDATA -and (Test-Path "$env:LOCALAPPDATA\Microsoft\WindowsApps")) {
        $targetDirs += "$env:LOCALAPPDATA\Microsoft\WindowsApps"
    }
    if ($scriptsDir -and (Test-Path $scriptsDir)) {
        $targetDirs += $scriptsDir
    }
    $banglaHome = "$HOME\.bangla\bin"
    New-Item -ItemType Directory -Force -Path $banglaHome | Out-Null
    $targetDirs += $banglaHome

    foreach ($dir in $targetDirs) {
        try {
            Set-Content -Path "$dir\bangla.cmd" -Value $cmdContent -Force -ErrorAction SilentlyContinue
            Set-Content -Path "$dir\bangla.bat" -Value $cmdContent -Force -ErrorAction SilentlyContinue
            Set-Content -Path "$dir\bangla.ps1" -Value $ps1Content -Force -ErrorAction SilentlyContinue
        } catch {}
    }

    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $newPaths = @($banglaHome)
    if ($scriptsDir) { $newPaths += $scriptsDir }

    foreach ($p in $newPaths) {
        if ($userPath -notlike "*$p*") { $userPath = "$userPath;$p" }
    }
    [Environment]::SetEnvironmentVariable("Path", $userPath, "User")
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + $userPath + ";$($targetDirs -join ';')"

    Write-Host ""
    Write-Host "==========================================================" -ForegroundColor Green
    Write-Host " [✓] অভিনন্দন! BanglaThon সম্পূর্ণ সফলভাবে প্রস্তুত হয়েছে!    " -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "এখন সরাসরি আপনার ফাইলে লিখুন ও রান করুন:" -ForegroundColor Yellow
    Write-Host "   bangla run tas.bl" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[!] স্বয়ংক্রিয় ইনস্টলেশনে সমস্যা হয়েছে। নিচের ২টির একটি সহজ উপায় করুন:" -ForegroundColor Red
    Write-Host "    উপায় ১: PowerShell-এ লিখুন: winget install Python.Python.3.12" -ForegroundColor Yellow
    Write-Host "    উপায় ২: PowerShell-এ শুধু 'python' লিখে এন্টার দিন, Microsoft Store খুললে 'Get/Install' চাপুন।" -ForegroundColor Yellow
    Write-Host ""
}
