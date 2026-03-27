# Slicer & Print Pipeline

## Software

- **Bambu Studio** - Official slicer (fork of PrusaSlicer), open source
- **OrcaSlicer** - Community fork with extra features (recommended for automation)

Both have CLI modes for headless slicing.

## Print Bed (Bambu A1 & P1S)

Both: **256 x 256 x 256 mm** build volume.
Practical max per panel: ~240 x 240 mm with margins.

## Automated Pipeline

```
Build123d (parametric) → export_3mf() → OrcaSlicer CLI → .gcode.3mf → Printer
```

### OrcaSlicer CLI
```bash
orca-slicer --slice 0 \
  --load-settings printer.json \
  --load-filament filament.json \
  --load-process process.json \
  --export-3mf output.3mf \
  input.stl
```

### Bambu LAN Printing (MQTT + FTPS)
- MQTT port 8883 for commands/status
- FTPS port 990 for file upload
- Access code from printer LCD: Network > Access Code
- Python: `paho-mqtt` + `ftplib.FTP_TLS`

## File Format

**3MF preferred** over STL for Bambu printers:
- Embeds units (mm), multi-material support, smaller files
- Build123d: `export_3mf()` native support

## Wing Panel Sizing (AeroForge: 2.56m wingspan)

10 panels total (5 per half-wing), each exactly 256mm span = full bed width.

| Panel | Span | Chord Range | Content |
|-------|------|-------------|---------|
| Root (P1) | 256mm | 210→191mm | Flap |
| Inner-mid (P2) | 256mm | 191→172mm | Flap |
| Mid (P3) | 256mm | 172→153mm | Flap/aileron transition |
| Outer-mid (P4) | 256mm | 153→134mm | Aileron |
| Tip (P5) | 256mm | 134→115mm | Aileron, wingtip cap |
