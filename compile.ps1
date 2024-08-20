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

    [string]$IconPath = ".\assets\images\icon.ico"
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

# Check if icon file exists
if (-not (Test-Path $IconPath)) {
    Write-Host "Warning: Icon file not found at $IconPath. Compilation will proceed without an icon."
    $iconFlag = ""
} else {
    $iconFlag = "--windows-icon-from-ico=`"$IconPath`""
}

# Build the Nuitka command
$nuitkaCommand = "python -m nuitka --standalone --plugin-enable=pyside6 --output-dir=`"$OutputDir`" --output-filename=`"$AppName.exe`" $iconFlag $AdditionalFlags `"$MainPyFile`""

# Execute Nuitka compilation
Write-Host "Compiling $MainPyFile with Nuitka..."
Write-Host "Command: $nuitkaCommand"
Invoke-Expression $nuitkaCommand

if ($LASTEXITCODE -ne 0) {
    Write-Host "Nuitka compilation failed. Please check the output for errors."
    exit 1
}

Write-Host "Nuitka compilation completed successfully."