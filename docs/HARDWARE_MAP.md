# Hardware map: courbet (Mi 11 Lite 4G) vs sweet (Redmi Note 10 Pro)
#
# Source: V14.0.4.0.TKQMIXM Global ROM
# - boot.img (Android DTS, partial)
# - dtbo.img -> 40 DTBO entries (overlay)
# All extracted under hw/firmware/{boot_unpacked, dtbo_dtbs/}

## Identical (same SoC SM7150, no changes needed)
| Item          | sweet | courbet |
|---------------|-------|---------|
| SoC           | SM7150 | SM7150 |
| GIC           | GICv3, 0x17a00000 (GICD) / 0x17a60000 (GICR) | same |
| Timer PPI     | INTID 19 (virtual) | same (armv8-timer: virt=3 => INTID 16+3=19) |
| UFS host      | 0x01d84000 (qcom,ufshc) | same |
| PMIC          | PM6150 + PM6150L, SPMI arbiter @ 0x200f000 | same |
| PON keys      | PM6150 PON @ SID0 0x810 (KPD_PWR/RESIN), vol+ @ PM6150L GPIO2 SID4 0xC110 | same |
| GCC/QUP base  | GCC 0x00100000, TLMM/NORTH 0x03900000 | same |
| DDR bank      | upper bank 0x100000000 + 0xfcc00000 (~4GB, 8GB unit) | same |

## Different (courbet-specific, changes needed)
| Item              | sweet                          | courbet                              |
|-------------------|--------------------------------|--------------------------------------|
| Touch IC          | Goodix GT9896, I2C 0x5d       | **Himax HX83112 ("himax,hxcommon"), I2C 0x48** |
| Touch QUP engine  | GENI SE7 (global)             | **QUPv3 SE1 I2C** (fragment@27 target) |
| Touch rail        | RPMh L11C                     | **PM6150 LDO10 (VDD) + PM6150L LDO7 (AVDD)** |
| Touch IRQ         | GPIO (in SE7 context)         | **TLMM GPIO 89** (fpc/himax irq, 0x59) |
| Touch RESET       | GPIO 8                        | **TLMM GPIO 88** (0x58) |
| Panel driver      | (in-kernel IOMFB)            | DSI RM69298 AMOLED video mode, 1080x2400, 90Hz |
| Splash FB base    | 0x9c000000 (cont_splash)      | **TBD - must be discovered on device** (not in DT) |
| Fingerprint       | -                            | FPC1020 (SPI, unused for iOS) |
| NFC               | -                            | ST NFC NQ @ 0x28 (I2C, on SE5) |

## Notes
1. The splash framebuffer physical address is NOT in the DTS/DTBO.
   ABL allocates it into a reserved-memory region at boot. We need to
   discover it on the device (dump /proc/device-tree/reserved-memory/
   on Android, or read it via the stock recovery). Until then we keep
   FB_BASE = 0x9c000000 as a reasonable guess for SM7150.

2. Touch on QUPv3 SE1: physical base of SE1 on SM7150 is 0x00a84000?
   NO - that's SE7. On SM7150 (qcom,qupv3 layout):
     SE0 0x08800000, SE1 0x08840000, SE2 0x08880000, SE3 0x088c0000,
     SE4 0x08900000, SE5 0x08940000, SE6 0x08980000, SE7 0x089c0000
   But sweet uses 0x00a84000 which is the *old QUPv2* SE7 base on
   SM7150 (dual-mapped). We must confirm which base SE1 I2C has on
   courbet from the live FDT. The DTBO only gives us the phandle name
   "qupv3_se1_i2c", not the register range.
   => Action: dump the live FDT on device, find /soc/i2c@XXXX "SE1".

3. The Himax HX83112 protocol is different from Goodix GT9896:
   - different ID registers, event status byte, and point report format
   - We must write a new protocol layer (touch_himax.c) inside
     sweet_touch.c, reusing the same GENI I2C FIFO engine + HID path.

## TODO checklist for this session
- [ ] Confirm QUPv3 SE1 I2C base address (need live FDT on device)
- [ ] Confirm splash framebuffer base (need live FDT or ABL config)
- [ ] Write xnu/patches/0082-courbet-himax-touch.patch
- [ ] Update shim/console.h + mmu.h if FB base differs
- [ ] Update tools/mkadt.py (FB, identity already done)
- [ ] Update tools/mkpayload.py / qemu-sweet.py magic if needed
- [ ] Provide flash + boot guide
