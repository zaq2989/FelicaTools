# FelicaTools

Miscellaneous FeliCa Tools

# Preparation

## device

any device can read

need RC-S380 to emulate

## nfcpy

[Getting started - nfcpy documentation](https://nfcpy.readthedocs.io/en/latest/topics/get-started.html)

`pip install nfcpy`

### Windows

Replace RC-S380 driver to WinUSB with [Zadig](https://zadig.akeo.ie/).

### Mac

TODO

### Linux

Nothing to do.

# Features

## Command

`python command.py`

send raw command from stdin i.e. `00 ffff 01 00`

## Dump

`python dump.py -o [FILE]`

## Emulate

`python emulate.py [FILE]`

## Format

dump and emulate use common [FeliCa-Format](https://github.com/OLIET2357/FeliCa-Format)
