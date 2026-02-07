param([string]$version = "")

$ErrorActionPreference = "Stop"

# Setup
if (!(Test-Path env)) {
    py -m venv env
}

$venvPython = ".\\env\\Scripts\\python.exe"
& $venvPython -m pip install --upgrade pip

$pyTag = (& $venvPython -c "import sys; print(f'cp{sys.version_info[0]}{sys.version_info[1]}')").Trim()
$lockFile = ".\\requirements.lock.py$($pyTag.Substring(2)).txt"

# Install dependencies
& $venvPython -m pip install -r requirements.build.txt
if (Test-Path $lockFile) {
    & $venvPython -m pip install -r $lockFile
}

# Read app version from source if not provided
if ([string]::IsNullOrWhiteSpace($version)) {
    $versionLine = Select-String -Path ".\\dwt_about.py" -Pattern '__version__\s*=\s*"([^"]+)"' | Select-Object -First 1
    if (-not $versionLine) {
        throw "Unable to resolve version from dwt_about.py"
    }
    $version = $versionLine.Matches[0].Groups[1].Value
}

# Clean
Remove-Item -Recurse -Force .\\build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\\dist -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\\public -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path .\\public | Out-Null

# Build
& $venvPython -m PyInstaller --clean --noconfirm --onefile --windowed --icon main.ico --name DisableWinTracking dwt.py

# Package
Copy-Item COPYING .\\dist\\
Copy-Item COPYING.LESSER .\\dist\\
Copy-Item README.md .\\dist\\

Compress-Archive -Force -Path .\\dist\\* -DestinationPath ".\\public\\dwt-$version-$pyTag-win_amd64.zip"
