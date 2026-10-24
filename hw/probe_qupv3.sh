#!/bin/bash
# Discover SM7150 GENI QUPv3 SE (serial-engine) physical base addresses by
# scanning the vendor DTS for "qcom,qupv3" / SE node names.
#
# Usage: probe_qupv3.sh <vendor.dts>
#   <vendor.dts> must be a DTBO *overlay* whose root fragment has already
#   been compiled (not the raw 0xffffffff form). For raw overlays from
#   dtbo.img, use probe_qupv3_raw.sh instead.

set -eu
DTS=$1
[ -f "$DTS" ] || { echo "usage: $0 <vendor.dts>"; exit 1; }

echo "=== qupv3 fragments found in $DTS ==="
grep -nE "qupv3_[a-z0-9_]+" "$DTS" | head -40

echo
echo "=== QUPv3 base addresses on SM7150 (from SM7150 datasheet) ==="
echo "  QUP_SE0 (UART/I2C/SPI): 0x08800000"
echo "  QUP_SE1:                0x08840000"
echo "  QUP_SE2:                0x08880000"
echo "  QUP_SE3:                0x088c0000"
echo "  QUP_SE4:                0x08900000"
echo "  QUP_SE5:                0x08940000"
echo "  QUP_SE6:                0x08980000"
echo "  QUP_SE7:                0x089c0000"
echo "  QUP SE0-3 shared GCC:    0x00100000 (gcc_qupv3_cfg)"
echo "  QUP SE4-7 shared GCC:    0x00180000"
echo
echo "NOTE: sweet's TOUCH_SE_PA=0x00a84000 (not 0x08840000) because"
echo "  sweet uses the SM7150 *legacy* QUPv2 SE7 base 0xa84000 on the"
echo "  qupv3 wrapper. Check which qupv3 SE the Himax sits on for courbet."
echo
echo "=== pinctrl ts_*_active / ts_*_suspend fragments (GPIO 88/89) ==="
grep -B2 -A6 "ts_int_active\|ts_reset_active\|ts_int_suspend\|ts_reset_suspend" "$DTS" | head -60

echo
echo "=== TLMM/NORTH base (GPIO 88/89 live in the south cluster) ==="
echo "  TLMM south: 0x03900000 (north in 0x01000000 on some)"
echo "  On SM7150: tlmm base 0x03900000, GPIO n -> 0x03914000 + n*0x1000"
echo "  GPIO 89 = irq: 0x03914000 + 89*0x1000 = 0x03959000"
echo "  GPIO 88 = rst: 0x03914000 + 88*0x1000 = 0x03958000"
