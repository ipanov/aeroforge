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

## Wing Panel Sizing (AeroForge: 2.1m wingspan)

6 panels total (3 per half-wing), each ~350mm span.
350mm fits comfortably on the 256mm bed printed at slight angle or with
chord axis along the shorter dimension (chord 110-200mm < 256mm).

| Panel | Span | Chord Range | Content |
|-------|------|-------------|---------|
| Root (Panel 1) | ~350mm | 200→177mm | Flap, 2 servos |
| Mid (Panel 2) | ~350mm | 177→132mm | Flap/aileron transition |
| Tip (Panel 3) | ~350mm | 132→110mm | Aileron, wingtip cap |
