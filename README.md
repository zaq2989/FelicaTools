# FelicaTools

Miscellaneous FeliCa Tools

# Preparation

## nfcpy

`pip install nfcpy`

[Getting started - nfcpy documentation](https://nfcpy.readthedocs.io/en/latest/topics/get-started.html)

### Windows

Replace RC-S380 driver to WinUSB with [Zadig](https://zadig.akeo.ie/).

### Mac

TODO

### Linux

Nothing to do.

# Features

## Dump

`python dump.py [FILE]`

## Emulate

`python emulate.py [DUMPFILE]`

Support dump files

- Output of `dump.py`
- Output of `tagtool.py -v show` (including `Memory Dump:`)
- Tagtool(TODO:link)

## Command

`python command.py`

send stdin command i.e. `0600ffff00`

## Relay

`python relay.py`

Require two devices
