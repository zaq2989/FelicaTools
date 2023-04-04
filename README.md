# FelicaTools

Miscellaneous FeliCa Tools

**🚧Under Construction🚧**

# Preparation

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

## Dump

`python dump.py -o [FILE]`

## Emulate

`python emulate.py [FILE]`

## Command (for developer)

`python command.py`

send command from stdin i.e. `00 ffff 01 00`

## Relay (for developer) (waiting refactoring)

`python relay.py`

Require two devices
