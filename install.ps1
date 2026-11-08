# BanglaThon Universal 1-Click Windows Standalone Installer
# Usage: irm https://raw.githubusercontent.com/tasfiqueofficial/BanglaThon/main/install.ps1 | iex

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   বাংলথন (BanglaThon) — উইন্ডোজ ইউনিভার্সাল ইনস্টলার       " -ForegroundColor Cyan
Write-Host "   (কোনো পাইথন ইনস্টলেশন ছাড়াই ১০০% সরাসরি চলবে!)          " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""

# Universal directory accessible by all users
$installDir = "C:\BanglaThon"
$runtimeDir = "$installDir\runtime"
$binDir = "$installDir\bin"

# Create directories
New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null
New-Item -ItemType Directory -Force -Path $binDir | Out-Null

# 1. Download Standalone Portable Runtime (~10MB) if not present
$pyExe = "$runtimeDir\python.exe"
if (-not (Test-Path $pyExe)) {
    Write-Host "[+] স্বয়ংক্রিয় পোর্টেবল ইঞ্জিন ডাউনলোড হচ্ছে (~১০ MB)..." -ForegroundColor Cyan
    $embedZipUrl = "https://www.python.org/ftp/python/3.12.3/python-3.12.3-embed-amd64.zip"
    $embedZipFile = "$env:TEMP\py_embed.zip"
    
    Invoke-WebRequest -Uri $embedZipUrl -OutFile $embedZipFile -UseBasicParsing
    Write-Host "[+] ইঞ্জিন আনপ্যাক করা হচ্ছে..." -ForegroundColor Cyan
    Expand-Archive -Path $embedZipFile -DestinationPath $runtimeDir -Force
    Remove-Item -Path $embedZipFile -Force

    # Enable site packages in python._pth
    $pthFile = Get-ChildItem -Path $runtimeDir -Filter "*._pth" | Select-Object -First 1
    if ($pthFile) {
        $content = Get-Content $pthFile.FullName
        $content = $content -replace '#import site', 'import site'
        if ($content -notcontains '.') { $content += "`r`n." }
        Set-Content -Path $pthFile.FullName -Value $content
    }
}

# 2. Download latest BanglaThon engine files
Write-Host "[+] BanglaThon কোর ফাইল যুক্ত করা হচ্ছে..." -ForegroundColor Cyan
$repoZipUrl = "https://github.com/tasfiqueofficial/BanglaThon/archive/refs/heads/main.zip"
$repoZipFile = "$env:TEMP\banglathon_core.zip"

Invoke-WebRequest -Uri $repoZipUrl -OutFile $repoZipFile -UseBasicParsing
$tempExtract = "$env:TEMP\bangla_extract"
if (Test-Path $tempExtract) { Remove-Item -Path $tempExtract -Recurse -Force }
Expand-Archive -Path $repoZipFile -DestinationPath $tempExtract -Force

Copy-Item -Path "$tempExtract\BanglaThon-main\*" -Destination $runtimeDir -Recurse -Force
Remove-Item -Path $repoZipFile -Force
Remove-Item -Path $tempExtract -Recurse -Force

# 3. Create Universal Launcher (Uses absolute path to portable engine - NO FAKE PYTHON ERROR!)
$cmdContent = "@echo off`r`n`"C:\BanglaThon\runtime\python.exe`" `"C:\BanglaThon\runtime\main.py`" %*"
$ps1Content = "param([Parameter(ValueFromRemainingArguments=`$true)]`$p)`r`n& `"C:\BanglaThon\runtime\python.exe`" `"C:\BanglaThon\runtime\main.py`" @p"

# Save in C:\BanglaThon\bin
Set-Content -Path "$binDir\bangla.cmd" -Value $cmdContent -Force
Set-Content -Path "$binDir\bangla.bat" -Value $cmdContent -Force
Set-Content -Path "$binDir\bangla.ps1" -Value $ps1Content -Force

# Also copy to C:\Windows (Guaranteed to be in PATH on 100% of all Windows machines!)
if (Test-Path "C:\Windows") {
    try {
        Set-Content -Path "C:\Windows\bangla.cmd" -Value $cmdContent -Force -ErrorAction SilentlyContinue
        Set-Content -Path "C:\Windows\bangla.bat" -Value $cmdContent -Force -ErrorAction SilentlyContinue
    } catch {}
}

# Remove any old conflicting stub in WindowsApps
if ($env:LOCALAPPDATA -and (Test-Path "$env:LOCALAPPDATA\Microsoft\WindowsApps\bangla.cmd")) {
    Remove-Item "$env:LOCALAPPDATA\Microsoft\WindowsApps\bangla.*" -Force -ErrorAction SilentlyContinue
}

# Add C:\BanglaThon\bin to System and User PATH
$machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if ($machinePath -notlike "*$binDir*") {
    try { [Environment]::SetEnvironmentVariable("Path", "$machinePath;$binDir", "Machine") } catch {}
}
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$binDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$binDir", "User")
}

# Update current active session
$env:Path = "$binDir;C:\Windows;$env:Path"

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host " [✓] অভিনন্দন! BanglaThon সফলভাবে প্রস্তুত হয়েছে!           " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "এখনই যেকোনো ফোল্ডারে (VS Code বা CMD-তে) সরাসরি চালান:" -ForegroundColor Yellow
Write-Host "   bangla run tas.bl" -ForegroundColor Cyan
Write-Host ""
Write-Host "অথবা সরাসরি লাইভ কনসোলে লিখুন:" -ForegroundColor Yellow
Write-Host "   bangla" -ForegroundColor Cyan
Write-Host ""
