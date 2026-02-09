# DisableWinTracking (Fork)

Living fork of the original archived project: <https://github.com/10se1ucgo/DisableWinTracking>.

Current upstream repository: <https://github.com/Potencial/DisableWinTracking>
Current app version: `v3.2.6`

![screenshot](web/dwt-screenshot.png)

## English

### Download

- Releases: <https://github.com/Potencial/DisableWinTracking/releases>

### Platform and Python Support

- Target OS: Windows 10 (some functionality may also work on Windows 11).
- Supported Python versions for source/runtime validation:
- Python `3.12`
- Python `3.14`

### Dependencies

Runtime dependency model:

- `requirements.lock.py312.txt`: reproducible runtime set for Python 3.12
- `requirements.lock.py314.txt`: reproducible runtime set for Python 3.14
- `requirements.txt`: editable runtime base (ranges)
- `requirements.build.txt`: build tooling (`PyInstaller` and hooks)

Install runtime dependencies (recommended):

```powershell
py -3.12 -m pip install -r requirements.lock.py312.txt
py -3.14 -m pip install -r requirements.lock.py314.txt
```

Install editable runtime base:

```powershell
py -3.14 -m pip install -r requirements.txt
```

### Running the App

Run GUI (as Administrator):

```powershell
py -3.14 dwt.py
```

Silent mode:

```powershell
py -3.14 dwt.py -silent
```

`-silent` currently applies these actions:

- Clear DiagTrack log (`clear_diagtrack`)
- Stop telemetry services (`dmwappushsvc`, `DiagTrack`)
- Set services to privacy state (`Start=4`)
- Set telemetry policy (`AllowTelemetry=0`)
- Apply WifiSense registry settings
- Apply OneDrive uninstall/privacy settings

`-silent` currently does **not** automatically apply:

- HOSTS domain blocking options
- IP blocking firewall rules
- Xbox DVR change
- Windows Defender collection option (disabled in UI)

### Features and Current Behavior

- Services:
- Service Method `Disable`: stops services and applies registry startup state.
- Service Method `Delete`: removes services; also writes service startup state keys when available.
- Mode `Privacy`: applies privacy settings.
- Mode `Revert`: reverts supported settings.
- Telemetry: writes `AllowTelemetry` under policy registry path.
- HOSTS blocking: uses selected domain lists from settings dialog.
- Extra HOSTS blocking: optional additional domains.
- IP blocking: creates/removes firewall rules per selected IPs.
- Windows Defender collection: present in UI but disabled by design.
- WifiSense: registry-based toggles.
- OneDrive: registry toggles + `OneDriveSetup.exe /uninstall` or `/install` depending on mode.
- Xbox DVR: registry-based enable/disable.

### Validation and CI

Local smoke validation script:

```powershell
./scripts/windows_smoke.ps1 -PythonVersion 3.12
./scripts/windows_smoke.ps1 -PythonVersion 3.14
```

From WSL, call Windows PowerShell:

```bash
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\windows_smoke.ps1 -PythonVersion 3.14
```

CI workflow:

- `.github/workflows/windows-smoke.yml`
- Executes smoke validations on Python `3.12` and `3.14`.

### Build and Release Artifacts

Build command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build.ps1
```

Expected outputs:

- `dist/DisableWinTracking.exe`
- `public/dwt-<version>-<pyTag>-win_amd64.zip`

### Historical Notes

- This fork preserved the NCSI fix that avoids adding these entries to HOSTS:
- `0.0.0.0 msftncsi.com`
- `0.0.0.0 www.msftncsi.com`

### Cyrillic Path Warning

This program may fail when executed from paths containing Cyrillic characters. Run from a non-Cyrillic path (for example `C:\`).

## Español

### Descarga

- Releases: <https://github.com/Potencial/DisableWinTracking/releases>

### Plataforma y soporte de Python

- SO objetivo: Windows 10 (parte de la funcionalidad también puede funcionar en Windows 11).
- Versiones soportadas para ejecución/validación desde código fuente:
- Python `3.12`
- Python `3.14`

### Dependencias

Modelo actual de dependencias:

- `requirements.lock.py312.txt`: entorno reproducible para Python 3.12
- `requirements.lock.py314.txt`: entorno reproducible para Python 3.14
- `requirements.txt`: base editable de runtime (rangos)
- `requirements.build.txt`: herramientas de build (`PyInstaller` y hooks)

Instalación recomendada (locks):

```powershell
py -3.12 -m pip install -r requirements.lock.py312.txt
py -3.14 -m pip install -r requirements.lock.py314.txt
```

Instalación base editable:

```powershell
py -3.14 -m pip install -r requirements.txt
```

### Ejecución

Modo gráfico (como Administrador):

```powershell
py -3.14 dwt.py
```

Modo silencioso:

```powershell
py -3.14 dwt.py -silent
```

Actualmente `-silent` aplica:

- Limpieza de DiagTrack (`clear_diagtrack`)
- Detención de servicios de telemetría (`dmwappushsvc`, `DiagTrack`)
- Estado de privacidad de servicios (`Start=4`)
- Política de telemetría (`AllowTelemetry=0`)
- Cambios de WifiSense
- Cambios de OneDrive (privacidad/desinstalación)

Actualmente `-silent` **no** aplica automáticamente:

- Bloqueo de dominios en HOSTS
- Bloqueo de IPs por firewall
- Cambio de Xbox DVR
- Opción de Windows Defender collection (deshabilitada en UI)

### Funcionalidades y comportamiento actual

- Servicios:
- Método `Disable`: detiene servicios y aplica estado de inicio en registro.
- Método `Delete`: elimina servicios y escribe claves de inicio cuando existan.
- Modo `Privacy`: aplica cambios de privacidad.
- Modo `Revert`: revierte cambios soportados.
- Telemetría: escritura en clave de política `AllowTelemetry`.
- HOSTS: usa las listas seleccionadas en el diálogo de configuración.
- HOSTS extra: conjunto adicional opcional.
- Bloqueo de IP: reglas de firewall por IP seleccionada.
- Windows Defender collection: visible pero deshabilitado por diseño.
- WifiSense: cambios por registro.
- OneDrive: cambios por registro + ejecución de `OneDriveSetup.exe`.
- Xbox DVR: cambios por registro.

### Validación y CI

Script local de validación:

```powershell
./scripts/windows_smoke.ps1 -PythonVersion 3.12
./scripts/windows_smoke.ps1 -PythonVersion 3.14
```

Desde WSL usando PowerShell de Windows:

```bash
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\windows_smoke.ps1 -PythonVersion 3.14
```

Workflow de CI:

- `.github/workflows/windows-smoke.yml`
- Ejecuta validación en Python `3.12` y `3.14`.

### Build y artefactos

Comando de build:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build.ps1
```

Salidas esperadas:

- `dist/DisableWinTracking.exe`
- `public/dwt-<version>-<pyTag>-win_amd64.zip`

### Nota histórica

Este fork conserva la corrección de NCSI para no añadir en HOSTS:

- `0.0.0.0 msftncsi.com`
- `0.0.0.0 www.msftncsi.com`

### Advertencia de rutas con caracteres cirílicos

La aplicación puede fallar si se ejecuta desde rutas con caracteres cirílicos. Ejecutar desde una ruta sin cirílico (por ejemplo `C:\`).

## License

This project remains under GPLv3 (see `COPYING`).
