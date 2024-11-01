# build.ps1
# PowerShell script to build NSIS installer for PySide6 application

# Configuration
$appName = "Turtle WoW Launcher"
# $appVersion = "1.0.0"
$mainPyFile = "__main__.py"
$outputDir = ".\build"
$nsisPath = "C:\Program Files (x86)\NSIS\makensis.exe"
$nsisScript = "installer.nsi"
$iconPath = ".\assets\images\icon.ico"

# Additional Nuitka flags
#$additionalNuitkaFlags = "--windows-disable-console"

# Step 1: Compile the application using Nuitka
Write-Host "Compiling application with Nuitka..."
.\compile.ps1 -MainPyFile $mainPyFile -OutputDir $outputDir -AppName $appName -AdditionalFlags $additionalNuitkaFlags -IconPath $iconPath

if ($LASTEXITCODE -ne 0) {
    Write-Host "Compilation failed. Exiting."
    exit 1
}

# Step 2: Build the installer using NSIS
Write-Host "Building installer with NSIS..."
$nsisCommand = "& '$nsisPath' '$nsisScript'"
Invoke-Expression $nsisCommand

if ($LASTEXITCODE -ne 0) {
    Write-Host "NSIS compilation failed. Exiting."
    exit 1
}

Write-Host "Installer build completed successfully."