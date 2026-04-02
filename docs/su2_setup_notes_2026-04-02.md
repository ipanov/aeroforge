# SU2 Setup Notes

Date: 2026-04-02

## Status

- Repo-local work tree left untouched.
- User-local SU2 source checkout staged at `C:\Users\ilija\aeroforge-tools\SU2`.
- Official dependency installers staged at `C:\Users\ilija\aeroforge-tools\SU2-installers`:
  - `mingw-w64-install.exe`
  - `msmpisetup.exe`
  - `msmpisdk.msi`
- No Windows build was completed yet.

## What I Checked

- Existing repo guidance in `CLAUDE.md`, `docs/aero_tools_catalog.md`, and `docs/tooling_analysis.md`.
- Local executable availability for:
  - `python`
  - `git`
  - `cmake`
  - `ninja`
  - `gcc`
  - `g++`
  - `mpicc`
  - `mpicxx`
  - `cl`
- Local GPU hardware via `Win32_VideoController`.
- Official SU2 docs and release notes:
  - Installation and build docs
  - Windows build docs
  - Latest release notes for GPU/CUDA status

## Official SU2 Basis

- SU2’s official installation docs recommend building from source for best compatibility and performance.
- The official Windows build guide says SU2 on Windows uses MinGW and Microsoft MPI.
- The latest release notes only describe CUDA/GPU acceleration as an experimental addition to the FGMRES linear solver, not full GPU CFD.

## What I Staged

- Cloned the official SU2 source repository to:
  - `C:\Users\ilija\aeroforge-tools\SU2`

## Missing On This Machine

- `cmake`
- a supported MinGW-w64 toolchain
- Microsoft MPI
- a verified SU2 build output

## Recommended Practical Path

1. Keep the staged source checkout.
2. Install MinGW-w64 and Microsoft MPI on Windows, then follow the official SU2 Windows build guide.
3. If the Windows toolchain path stays brittle, build in WSL2/Linux instead, still from the official SU2 source tree.

## Verification Command

After a successful build, verify from the SU2 build output directory with:

```powershell
SU2_CFD.exe -h
```

If the Python wrapper is built, also verify with:

```powershell
python -c "import SU2"
```

## GPU Reality

- The machine does have an `NVIDIA GeForce RTX 3070`.
- Official SU2 documentation does not support the idea of full GPU-accelerated CFD on this machine today.
- The official release notes only document CUDA/GPU acceleration for the FGMRES linear solver, and mark it experimental.
- So: full SU2-on-GPU CFD is not a realistic expectation right now; only limited GPU acceleration is officially indicated.

## Blockers Remaining

- Missing Windows build dependencies.
- No confirmed official Windows binary install for the current SU2 line was staged.
- No validated build or runtime check has been completed yet.
