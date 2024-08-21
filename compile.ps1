# compile.ps1
# PowerShell script to compile a PySide6 application using Nuitka

param (
    [Parameter(Mandatory=$true)]
    [string]$MainPyFile,

    [Parameter(Mandatory=$true)]
    [string]$OutputDir,

    [Parameter(Mandatory=$true)]
    [string]$AppName,

    [string]$AdditionalFlags = "",

    [string]$IconPath = ".\assets\images\icon.ico",

    [switch]$EnableConsole
)

# Ensure Nuitka is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not found in PATH. Please ensure Python is installed and added to PATH."
    exit 1
}

# Check if Nuitka is installed
$nuitkaInstalled = python -c "import nuitka" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Nuitka is not installed. Installing Nuitka..."
    python -m pip install nuitka
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install Nuitka. Please install it manually using 'pip install nuitka'."
        exit 1
    }
}

# Ensure output directory exists
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

# Build the Nuitka command
$nuitkaCommand = @(
    "python -m nuitka",
    "--standalone",
    "--plugin-enable=pyside6",
    "--output-dir=`"$OutputDir`"",
    "--output-filename=`"$AppName.exe`""
    "--windows-disable-console"
)

if (Test-Path $IconPath) {
    $nuitkaCommand += "--windows-icon-from-ico=`"$IconPath`""
}

# Add PySide6 specific flags
$nuitkaCommand += @(
    "--enable-plugin=pyside6",
    "--include-qt-plugins=all",
    "--include-data-dir=.\assets=assets"
)

# Add any additional flags
if ($AdditionalFlags) {
    $nuitkaCommand += $AdditionalFlags
}

# Add the main Python file at the end
$nuitkaCommand += "`"$MainPyFile`""

# Join the command parts
$nuitkaCommandString = $nuitkaCommand -join " "

# Execute Nuitka compilation
Write-Host "Compiling $MainPyFile with Nuitka..."
Write-Host "Command: $nuitkaCommandString"
Invoke-Expression $nuitkaCommandString

if ($LASTEXITCODE -ne 0) {
    Write-Host "Nuitka compilation failed. Please check the output for errors."
    exit 1
}

Write-Host "Nuitka compilation completed successfully."