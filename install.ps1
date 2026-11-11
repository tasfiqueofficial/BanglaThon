# BanglaThon Universal 1-Click Windows Standalone Installer
# Usage: irm https://raw.githubusercontent.com/tasfiqueofficial/BanglaThon/main/install.ps1 | iex

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   বাংলথন (BanglaThon) — উইন্ডোজ ইউনিভার্সাল ইনস্টলার       " -ForegroundColor Cyan
Write-Host "   (কোনো পাইথন ইনস্টলেশন ছাড়াই ১০০% সরাসরি চলবে!)          " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""

# 1. Determine writable directory (C:\BanglaThon or %USERPROFILE%\.bangla)
$installDir = "C:\BanglaThon"
try {
    New-Item -ItemType Directory -Force -Path $installDir -ErrorAction Stop | Out-Null
} catch {
    $installDir = "$HOME\.bangla"
    New-Item -ItemType Directory -Force -Path $installDir -ErrorAction Stop | Out-Null
}

$runtimeDir = "$installDir\runtime"
$binDir = "$installDir\bin"

New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null
New-Item -ItemType Directory -Force -Path $binDir | Out-Null

# 2. Download Standalone Portable Runtime (~10MB) if not present
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

# 3. Download latest BanglaThon engine files
Write-Host "[+] BanglaThon কোর ইঞ্জিন ফাইল যুক্ত করা হচ্ছে..." -ForegroundColor Cyan
$repoZipUrl = "https://github.com/tasfiqueofficial/BanglaThon/archive/refs/heads/main.zip"
$repoZipFile = "$env:TEMP\banglathon_core.zip"

Invoke-WebRequest -Uri $repoZipUrl -OutFile $repoZipFile -UseBasicParsing
$tempExtract = "$env:TEMP\bangla_extract"
if (Test-Path $tempExtract) { Remove-Item -Path $tempExtract -Recurse -Force }
Expand-Archive -Path $repoZipFile -DestinationPath $tempExtract -Force

Copy-Item -Path "$tempExtract\BanglaThon-main\*" -Destination $runtimeDir -Recurse -Force
Remove-Item -Path $repoZipFile -Force
Remove-Item -Path $tempExtract -Recurse -Force

# 4. Clean up any conflicting .ps1 files that trigger PowerShell ExecutionPolicy
Remove-Item "$binDir\bangla.ps1" -Force -ErrorAction SilentlyContinue
Remove-Item "C:\BanglaThon\bin\bangla.ps1" -Force -ErrorAction SilentlyContinue
Remove-Item "$HOME\.bangla\bin\bangla.ps1" -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Windows\bangla.ps1" -Force -ErrorAction SilentlyContinue
if ($env:LOCALAPPDATA) {
    Remove-Item "$env:LOCALAPPDATA\Microsoft\WindowsApps\bangla.ps1" -Force -ErrorAction SilentlyContinue
}

# 5. Create Universal CMD & BAT Launchers (Exempt from PowerShell ExecutionPolicy)
$cmdContent = @"
@echo off
chcp 65001 >nul 2>&1
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
if exist "C:\BanglaThon\runtime\python.exe" (
    "C:\BanglaThon\runtime\python.exe" "C:\BanglaThon\runtime\main.py" %*
) else (
    "%USERPROFILE%\.bangla\runtime\python.exe" "%USERPROFILE%\.bangla\runtime\main.py" %*
)
"@

Set-Content -Path "$binDir\bangla.cmd" -Value $cmdContent -Force
Set-Content -Path "$binDir\bangla.bat" -Value $cmdContent -Force

# 6. Compile Native bangla.exe using built-in Windows .NET compiler (No external compiler needed)
$csharp = @"
using System;
using System.Diagnostics;
using System.IO;
using System.Text;

class BanglaApp {
    static int Main(string[] args) {
        try {
            Console.OutputEncoding = Encoding.UTF8;
            Console.InputEncoding = Encoding.UTF8;
        } catch {}

        string py = @"C:\BanglaThon\runtime\python.exe";
        string script = @"C:\BanglaThon\runtime\main.py";
        if (!File.Exists(py)) {
            string userProfile = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            py = Path.Combine(userProfile, @".bangla\runtime\python.exe");
            script = Path.Combine(userProfile, @".bangla\runtime\main.py");
        }
        if (!File.Exists(py)) {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine("[Error] BanglaThon engine not found. Please run installer again.");
            Console.ResetColor();
            return 1;
        }
        ProcessStartInfo psi = new ProcessStartInfo();
        psi.FileName = py;
        psi.EnvironmentVariables["PYTHONUTF8"] = "1";
        psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";
        string fullArgs = "\"" + script + "\"";
        foreach (string a in args) {
            fullArgs += " \"" + a + "\"";
        }
        psi.Arguments = fullArgs;
        psi.UseShellExecute = false;
        try {
            Process p = Process.Start(psi);
            p.WaitForExit();
            return p.ExitCode;
        } catch (Exception ex) {
            Console.WriteLine("[Error] " + ex.Message);
            return 1;
        }
    }
}
"@

try {
    Add-Type -TypeDefinition $csharp -OutputAssembly "$binDir\bangla.exe" -OutputType ConsoleApplication -ErrorAction SilentlyContinue
} catch {}

# Copy launchers to multiple search locations for maximum compatibility
$launcherLocations = @()
if ($env:LOCALAPPDATA -and (Test-Path "$env:LOCALAPPDATA\Microsoft\WindowsApps")) {
    $launcherLocations += "$env:LOCALAPPDATA\Microsoft\WindowsApps"
}
if (Test-Path "C:\Windows") {
    $launcherLocations += "C:\Windows"
}

foreach ($loc in $launcherLocations) {
    try {
        Set-Content -Path "$loc\bangla.cmd" -Value $cmdContent -Force -ErrorAction SilentlyContinue
        Set-Content -Path "$loc\bangla.bat" -Value $cmdContent -Force -ErrorAction SilentlyContinue
        if (Test-Path "$binDir\bangla.exe") {
            Copy-Item "$binDir\bangla.exe" "$loc\bangla.exe" -Force -ErrorAction SilentlyContinue
        }
    } catch {}
}

# 7. Add $binDir to User and System PATH permanently
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$binDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$binDir", "User")
}
try {
    $machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($machinePath -notlike "*$binDir*") {
        [Environment]::SetEnvironmentVariable("Path", "$machinePath;$binDir", "Machine")
    }
} catch {}

# 8. Update current active terminal session PATH immediately
$env:Path = "$binDir;C:\Windows;$env:LOCALAPPDATA\Microsoft\WindowsApps;$env:Path"

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host " [✓] অভিনন্দন! BanglaThon সফলভাবে প্রস্তুত হয়েছে!           " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "এখনই আপনার যেকোনো ফোল্ডারে (VS Code বা টার্মিনালে) চালান:" -ForegroundColor Yellow
Write-Host "   bangla run tas.bl" -ForegroundColor Cyan
Write-Host ""
Write-Host "অথবা সরাসরি লাইভ কনসোলে লিখুন:" -ForegroundColor Yellow
Write-Host "   bangla" -ForegroundColor Cyan
Write-Host ""
