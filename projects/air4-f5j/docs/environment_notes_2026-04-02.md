# Shell Environment Notes (2026-04-02)

## Problem

Inside this Codex shell session, external executables were failing to launch even when the files existed. Symptoms included failures launching:
- `python`
- `git`
- `cmd.exe`

The failure pattern was broader than Python itself.

## Root Cause In This Session

The shell environment was missing or corrupt for key Windows process-launch variables:
- `SystemRoot` was empty
- `ComSpec` was empty
- `PATHEXT` had degraded to `.CPL`
- user-home variables were also missing when Python libraries tried to resolve a config directory:
  - `HOME`
  - `USERPROFILE`
  - `HOMEDRIVE`
  - `HOMEPATH`

That explains why built-in PowerShell commands worked while external executables failed.

## Session-Local Fix

Running the following before external tools restored normal behavior in this session:

```powershell
$env:SystemRoot = 'C:\Windows'
$env:ComSpec = 'C:\Windows\System32\cmd.exe'
$env:PATHEXT = '.COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC;.CPL'
$env:USERPROFILE = 'C:\Users\ilija'
$env:HOME = 'C:\Users\ilija'
$env:HOMEDRIVE = 'C:'
$env:HOMEPATH = '\Users\ilija'
```

After that, the following worked again:

```powershell
python --version
git --version
python scripts\draw_iva_assembly.py
```

## Notes

- This fix is session-local, not a permanent machine-wide repair.
- If the Codex shell starts with the same broken environment again, re-apply the variables above before running Python, Git, or other executables.
