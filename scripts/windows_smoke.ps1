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

    $pyLauncher = $null
    $createdWithPy = $false
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $pyLauncher = "py"
    } elseif (Test-Path "C:\\Windows\\py.exe") {
        $pyLauncher = "C:\\Windows\\py.exe"
    }

    if ($pyLauncher) {
        try {
            & $pyLauncher -$TargetVersion -c "import sys" | Out-Null
            & $pyLauncher -$TargetVersion -m venv $TargetDir
            $createdWithPy = $true
        } catch {
            $createdWithPy = $false
        }
    }

    if (-not $createdWithPy) {
        if (Get-Command python -ErrorAction SilentlyContinue) {
            python -m venv $TargetDir
        } else {
            throw "Unable to create venv for Python $TargetVersion. Neither py launcher nor python executable was found."
        }
    }
}

if (!(Test-Path $pythonExe)) {
    New-RequestedVenv -TargetVersion $PythonVersion -TargetDir $venvDir
} else {
    $resolvedVersionOutput = & $pythonExe -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"
    $resolvedVersion = if ($null -eq $resolvedVersionOutput) { $PythonVersion } else { $resolvedVersionOutput.Trim() }
    if ($resolvedVersion -ne $PythonVersion) {
        Remove-Item -Recurse -Force $venvDir
        New-RequestedVenv -TargetVersion $PythonVersion -TargetDir $venvDir
    }
}

$resolvedVersionOutput = & $pythonExe -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"
$resolvedVersion = if ($null -eq $resolvedVersionOutput) { $PythonVersion } else { $resolvedVersionOutput.Trim() }
if ($resolvedVersion -ne $PythonVersion) {
    throw "Expected Python $PythonVersion but resolved $resolvedVersion"
}

& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r $lockFile

& $pythonExe -m py_compile dwt.py dwt_util.py dwt_about.py dwt_i18n.py

& $pythonExe -c "import wx, pywintypes, win32serviceutil, six; import dwt, dwt_util, dwt_about; print('Import smoke test passed')"

& $pythonExe -m unittest discover -s tests -p "test_*.py" -v
