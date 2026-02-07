param([string]$PythonVersion = "3.14")

$ErrorActionPreference = "Stop"

$venvSuffix = $PythonVersion.Replace('.', '')
$venvDir = ".\\.venv$venvSuffix"
$pythonExe = Join-Path $venvDir "Scripts\\python.exe"
$lockFile = ".\\requirements.lock.py$venvSuffix.txt"

if (!(Test-Path $lockFile)) {
    throw "Missing lock file: $lockFile"
}

function New-RequestedVenv {
    param([string]$TargetVersion, [string]$TargetDir)

    $createdWithPy = $false
    if (Get-Command py -ErrorAction SilentlyContinue) {
        try {
            py -$TargetVersion -c "import sys" | Out-Null
            py -$TargetVersion -m venv $TargetDir
            $createdWithPy = $true
        } catch {
            $createdWithPy = $false
        }
    }

    if (-not $createdWithPy) {
        python -m venv $TargetDir
    }
}

if (!(Test-Path $pythonExe)) {
    New-RequestedVenv -TargetVersion $PythonVersion -TargetDir $venvDir
} else {
    $resolvedVersion = (& $pythonExe -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')").Trim()
    if ($resolvedVersion -ne $PythonVersion) {
        Remove-Item -Recurse -Force $venvDir
        New-RequestedVenv -TargetVersion $PythonVersion -TargetDir $venvDir
    }
}

$resolvedVersion = (& $pythonExe -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')").Trim()
if ($resolvedVersion -ne $PythonVersion) {
    throw "Expected Python $PythonVersion but resolved $resolvedVersion"
}

& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r $lockFile

& $pythonExe -m py_compile dwt.py dwt_util.py dwt_about.py

& $pythonExe -c "import wx, pywintypes, win32serviceutil, six; import dwt, dwt_util, dwt_about; print('Import smoke test passed')"

& $pythonExe -m unittest discover -s tests -p "test_*.py" -v
