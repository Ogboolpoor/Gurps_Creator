# GURPS Character Sheet Builder

A desktop app for building **GURPS 4th edition** character sheets. Attributes and
secondary characteristics update live, a points budget tracks spending against
GURPS costs, and you can add a portrait and export the finished sheet to PNG or PDF.

## Run it (Windows - no install needed)

Just double-click an app:

| File | Language |
|------|----------|
| `GURPS-Sheet-EN.exe` | English |
| `GURPS-Sheet-RU.exe` | Russian |

Each `.exe` is fully self-contained (~18 MB). No Python required. The first launch
is a few seconds slower while it unpacks itself — this is normal.

## Run from source (any OS with Python 3)

```bash
python -m pip install pillow
python main_en.py    # English
python main_ru.py    # Russian
```

## Files

| File | Purpose |
|------|---------|
| `gurps_character_sheet.py` | The full application (all logic + GUI) |
| `main_en.py` / `main_ru.py` | Tiny launchers that start it in each language |
| `GURPS-Sheet-EN.exe` / `GURPS-Sheet-RU.exe` | Standalone Windows builds |

## Features

- Live-updating primary attributes (ST / DX / IQ / HT) and all secondary
  characteristics (HP, Will, Per, FP, Basic Speed/Move, Dodge, Lift, thrust/swing).
- Points budget with a detailed breakdown and custom point sources.
- Clickable portrait slot, scrollable panels, fantasy styling.
- Export to **PNG** / **PDF**, and save/load characters as JSON.
