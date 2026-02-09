# Contributing / Contribuciones

## English

### Scope

This document defines the minimum technical and documentation requirements for contributions.
It intentionally focuses on code quality, validation, and documentation consistency.

### Change Conventions

- Keep changes focused and atomic.
- Prefer explicit, descriptive commit messages.
- Do not mix unrelated refactors with functional fixes.
- If behavior changes, update docs in the same change set.

### Local Validation Requirements

Before opening a PR, run at least:

```powershell
python -m py_compile dwt.py dwt_util.py dwt_about.py
python -m unittest tests.test_dwt_util -v
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows_smoke.ps1 -PythonVersion 3.12
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows_smoke.ps1 -PythonVersion 3.14
```

### Build Validation (when packaging/build logic changes)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build.ps1
```

Expected outputs:

- `dist/DisableWinTracking.exe`
- `public/dwt-<version>-<pyTag>-win_amd64.zip`

### Documentation Policy

Any functional change that affects behavior, setup, validation, build, or troubleshooting must include documentation updates in the same PR, at minimum:

- `README.md`
- `.github/ISSUE_TEMPLATE.md` (if issue reproduction data needs change)
- `CONTRIBUTING.md` (if contributor workflow changes)

### PR Quality Checklist

- [ ] No break in declared runtime compatibility (Python 3.12/3.14).
- [ ] Commands documented in README exist and were validated.
- [ ] Tests/smoke checks run and results are reflected in PR notes.
- [ ] Documentation and code are consistent.
- [ ] No unrelated generated artifacts included unless necessary.

## Español

### Alcance

Este documento define los requisitos mínimos técnicos y documentales para contribuir.
Está centrado en calidad de cambios, validación y consistencia de documentación.

### Convenciones de cambios

- Mantener cambios acotados y atómicos.
- Usar mensajes de commit claros y descriptivos.
- No mezclar refactors no relacionados con fixes funcionales.
- Si cambia el comportamiento, actualizar documentación en el mismo set de cambios.

### Validación local requerida

Antes de abrir un PR, ejecutar como mínimo:

```powershell
python -m py_compile dwt.py dwt_util.py dwt_about.py
python -m unittest tests.test_dwt_util -v
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows_smoke.ps1 -PythonVersion 3.12
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows_smoke.ps1 -PythonVersion 3.14
```

### Validación de build (cuando cambie packaging/build)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build.ps1
```

Salidas esperadas:

- `dist/DisableWinTracking.exe`
- `public/dwt-<version>-<pyTag>-win_amd64.zip`

### Política de documentación

Todo cambio funcional que impacte comportamiento, setup, validación, build o troubleshooting debe incluir actualización documental en el mismo PR, al menos en:

- `README.md`
- `.github/ISSUE_TEMPLATE.md` (si cambian datos necesarios para reproducir issues)
- `CONTRIBUTING.md` (si cambia el flujo de contribución)

### Checklist de calidad para PR

- [ ] No romper compatibilidad declarada (Python 3.12/3.14).
- [ ] Los comandos documentados en README existen y se validaron.
- [ ] Tests/smoke ejecutados y resultados reportados en notas del PR.
- [ ] Coherencia entre documentación y código.
- [ ] No incluir artefactos generados no relacionados, salvo necesidad explícita.
