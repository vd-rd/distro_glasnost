# Glasnost AA13

Distro configuration for the [VD-RD Allwinner A13 SBC](https://github.com/vd-rd/sbc_allwinner_a13).

## Hardware Specifications

- **CPU**: Allwinner A13 (ARM Cortex-A8 @ 1GHz)
- **Memory**: 512MB DDR3
- **Storage**: microSD card
- **Connectivity**: RTL8188CUS WiFi (USB)
- **Dimensions**: 80mm x 42mm
- **Interfaces**: USB OTG, LCD (18-bit parallel), UART, I2C, SPI, GPIO

## Board Configuration

This directory contains the build configuration for Glasnost on the AA13 hardware:

- `spec.yaml` - Hardware specification
- `config/` - Kernel and U-Boot defconfigs
- `dts/` - Device tree source files
- `recipe/` - Image generation recipes (main and recovery)

## Image Layout

The SD card image includes:
- U-Boot bootloader @ 8KB offset (512KB)
- Boot partition (FAT32, 32MB) - kernel and device tree
- Root filesystem (XFS, 1GB)

## Compatible Hardware

This configuration targets the VD-RD A13 SBC. Additional DTB overlays for various hardware hats (LCD, GPS, GSM) are available in the `dts/` folder.

For hardware design files and schematics, see the [upstream repository](https://github.com/vd-rd/sbc_allwinner_a13).
