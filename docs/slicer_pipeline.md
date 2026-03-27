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

## Wing Panel Sizing

| Wingspan | Panels/half | Panel span | Total panels |
|----------|------------|------------|-------------|
| 1.0m | 2 | 250mm | 4 |
| 1.5m | 3 | 250mm | 6 |
| 1.8m | 4 | 225mm | 8 |
| 2.0m | 4 | 250mm | 8 |
