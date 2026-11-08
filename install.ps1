# BanglaThon One-Click Windows PowerShell Installer
# Usage: irm https://raw.githubusercontent.com/tasfiqueofficial/BanglaThon/main/install.ps1 | iex

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "   বাংলথন (BanglaThon) — উইন্ডোজ স্বয়ংক্রিয় ইনস্টলার    " -ForegroundColor Cyan
Write-Host "   বাংলা ভাষার নিজস্ব প্রোগ্রামিং ল্যাঙ্গুয়েজ ও ইন্টারপ্রেটার " -ForegroundColor Yellow
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""

# Check for Python in system
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command py -ErrorAction SilentlyContinue
}

if ($pythonCmd) {
    Write-Host "[+] আপনার কম্পিউটারে পাইথন পাওয়া গেছে!" -ForegroundColor Green
    Write-Host "[+] BanglaThon ডাউনলোড ও গ্লোবালি ইনস্টল করা হচ্ছে..." -ForegroundColor Cyan
    
    try {
        & $pythonCmd.Source -m pip install git+https://github.com/tasfiqueofficial/BanglaThon.git --quiet
        
        # Auto-detect Python Scripts directory and add to PATH if missing
        $scriptsDir = (& $pythonCmd.Source -c "import sysconfig; print(sysconfig.get_path('scripts'))" 2>$null).Trim()
        if ($scriptsDir -and (Test-Path $scriptsDir)) {
            $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
            if ($userPath -notlike "*$scriptsDir*") {
                [Environment]::SetEnvironmentVariable("Path", "$userPath;$scriptsDir", "User")
                Write-Host "[+] Python Scripts ফোল্ডার Windows PATH-এ স্বয়ংক্রিয়ভাবে যুক্ত করা হয়েছে।" -ForegroundColor Green
            }
            # Refresh current PowerShell session PATH immediately
            $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User") + ";$scriptsDir"
        }

        Write-Host ""
        Write-Host "======================================================" -ForegroundColor Green
        Write-Host " [✓] অভিনন্দন! BanglaThon সফলভাবে ইনস্টল হয়েছে!        " -ForegroundColor Green
        Write-Host "======================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "যেভাবে ফাইল রান করবেন:" -ForegroundColor Yellow
        Write-Host "  1. রান করুন: bangla run apnar_file.bl" -ForegroundColor Cyan
        Write-Host "  2. সরাসরি কোড লিখতে চালান: bangla" -ForegroundColor Cyan
        Write-Host "  3. যদি 'bangla' না পায়, তবে টার্মিনালটি বন্ধ করে নতুন করে খুলুন," -ForegroundColor White
        Write-Host "     অথবা সরাসরি চালান: python -m bangla_lang run apnar_file.bl" -ForegroundColor White
        Write-Host ""
    } catch {
        Write-Host "[!] ত্রুটি: pip ইনস্টলেশনে সমস্যা হয়েছে — $_" -ForegroundColor Red
    }
} else {
    Write-Host "[!] কম্পিউটারে পূর্বে কোনো পাইথন ইনস্টল পাওয়া যায়নি।" -ForegroundColor Yellow
    Write-Host "[+] উইন্ডোজ পোর্টেবল বাংলাথন এনভায়রনমেন্ট কনফিগার করা হচ্ছে..." -ForegroundColor Cyan

    $installDir = "$HOME\.bangla"
    $binDir = "$installDir\bin"
    New-Item -ItemType Directory -Force -Path $binDir | Out-Null

    # Download source zip
    $zipUrl = "https://github.com/tasfiqueofficial/BanglaThon/archive/refs/heads/main.zip"
    $zipFile = "$env:TEMP\banglathon_tmp.zip"
    
    Write-Host "[+] প্যাকেজ ডাউনলোড হচ্ছে..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile -UseBasicParsing
    
    Expand-Archive -Path $zipFile -DestinationPath $installDir -Force
    Remove-Item -Path $zipFile -Force

    # Ensure bin directory is in user PATH
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$binDir*") {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$binDir", "User")
        Write-Host "[+] উইন্ডোজ PATH-এ বাংলাথন যুক্ত করা হয়েছে।" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host " [✓] BanglaThon স্বয়ংক্রিয়ভাবে প্রস্তুত হয়েছে!           " -ForegroundColor Green
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "এখন নতুন যেকোনো CMD / PowerShell উইন্ডো খুলে লিখুন:" -ForegroundColor Yellow
    Write-Host "  bangla run code.bl" -ForegroundColor Cyan
    Write-Host ""
}
