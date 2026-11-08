# BanglaThon 100% Standalone Windows Portable Installer (NO PYTHON NEEDED!)
# Usage: irm https://raw.githubusercontent.com/tasfiqueofficial/BanglaThon/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   বাংলথন (BanglaThon) — স্ট্যান্ডঅ্যালন উইন্ডোজ ইনস্টলার    " -ForegroundColor Cyan
Write-Host "   (কোনো পাইথন ইনস্টলেশন ছাড়াই সরাসরি রান করবে!)          " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""

$installDir = "$HOME\.bangla"
$runtimeDir = "$installDir\runtime"
$binDir = "$installDir\bin"

# Create directories
New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null
New-Item -ItemType Directory -Force -Path $binDir | Out-Null

# 1. Download Standalone Portable Runtime (only ~10MB) if not present
$pyExe = "$runtimeDir\python.exe"
if (-not (Test-Path $pyExe)) {
    Write-Host "[+] স্বয়ংক্রিয় পোর্টেবল ইঞ্জিন ডাউনলোড হচ্ছে (~১০ MB)..." -ForegroundColor Cyan
    $embedZipUrl = "https://www.python.org/ftp/python/3.12.3/python-3.12.3-embed-amd64.zip"
    $embedZipFile = "$env:TEMP\py_embed.zip"
    
    Invoke-WebRequest -Uri $embedZipUrl -OutFile $embedZipFile -UseBasicParsing
    Write-Host "[+] ইঞ্জিন আনপ্যাক করা হচ্ছে..." -ForegroundColor Cyan
    Expand-Archive -Path $embedZipFile -DestinationPath $runtimeDir -Force
    Remove-Item -Path $embedZipFile -Force

    # Enable site packages in python._pth if present
    $pthFile = Get-ChildItem -Path $runtimeDir -Filter "*._pth" | Select-Object -First 1
    if ($pthFile) {
        $content = Get-Content $pthFile.FullName
        $content = $content -replace '#import site', 'import site'
        if ($content -notcontains '.') { $content += "`r`n." }
        Set-Content -Path $pthFile.FullName -Value $content
    }
}

# 2. Download latest BanglaThon engine files directly into runtime
Write-Host "[+] BanglaThon লেক্সার, পার্সার ও ইন্টারপ্রেটার যুক্ত করা হচ্ছে..." -ForegroundColor Cyan
$repoZipUrl = "https://github.com/tasfiqueofficial/BanglaThon/archive/refs/heads/main.zip"
$repoZipFile = "$env:TEMP\banglathon_core.zip"

Invoke-WebRequest -Uri $repoZipUrl -OutFile $repoZipFile -UseBasicParsing
$tempExtract = "$env:TEMP\bangla_extract"
if (Test-Path $tempExtract) { Remove-Item -Path $tempExtract -Recurse -Force }
Expand-Archive -Path $repoZipFile -DestinationPath $tempExtract -Force

# Copy core files to runtime folder
Copy-Item -Path "$tempExtract\BanglaThon-main\*" -Destination $runtimeDir -Recurse -Force
Remove-Item -Path $repoZipFile -Force
Remove-Item -Path $tempExtract -Recurse -Force

# 3. Create Universal Launcher Wrappers
$cmdContent = "@echo off`r`n`"%USERPROFILE%\.bangla\runtime\python.exe`" `"%USERPROFILE%\.bangla\runtime\main.py`" %*"
$ps1Content = "param([Parameter(ValueFromRemainingArguments=`$true)]`$p)`r`n& `"`$HOME\.bangla\runtime\python.exe`" `"`$HOME\.bangla\runtime\main.py`" @p"

# Write bangla.cmd and bangla.ps1 to $binDir
Set-Content -Path "$binDir\bangla.cmd" -Value $cmdContent -Force
Set-Content -Path "$binDir\bangla.bat" -Value $cmdContent -Force
Set-Content -Path "$binDir\bangla.ps1" -Value $ps1Content -Force

# Also write directly to WindowsApps (Guaranteed to be in PATH on all Windows 10/11)
if ($env:LOCALAPPDATA -and (Test-Path "$env:LOCALAPPDATA\Microsoft\WindowsApps")) {
    try {
        Set-Content -Path "$env:LOCALAPPDATA\Microsoft\WindowsApps\bangla.cmd" -Value $cmdContent -Force -ErrorAction SilentlyContinue
        Set-Content -Path "$env:LOCALAPPDATA\Microsoft\WindowsApps\bangla.bat" -Value $cmdContent -Force -ErrorAction SilentlyContinue
    } catch {}
}

# 4. Add to Windows User PATH permanently
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$binDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$binDir", "User")
}

# 5. Refresh CURRENT active PowerShell session PATH immediately!
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User") + ";$binDir"
if ($env:LOCALAPPDATA) { $env:Path += ";$env:LOCALAPPDATA\Microsoft\WindowsApps" }

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host " [✓] অভিনন্দন! আপনার পিসিতে পাইথন ছাড়াই BanglaThon প্রস্তুত! " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "এখনই আপনার ফোল্ডারে টার্মিনাল/VS Code-এ সরাসরি চালান:" -ForegroundColor Yellow
Write-Host "   bangla run tas.bl" -ForegroundColor Cyan
Write-Host ""
Write-Host "অথবা লাইভ কনসোলে সরাসরি কোড লিখতে চালান:" -ForegroundColor Yellow
Write-Host "   bangla" -ForegroundColor Cyan
Write-Host ""
