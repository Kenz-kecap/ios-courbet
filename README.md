# ios-courbet

iOS 16 userland on the Xiaomi Mi 11 Lite 4G ("courbet", M2101K9AG,
Qualcomm SM7150 / Snapdragon 732G).

This is a port of [dipa-studio/ios-sweet](https://github.com/dipa-studio/ios-sweet)
(Redmi Note 10 Pro, also SM7150) to courbet.

## Status: WORKING PROGRESS

The sweet repo's XNU kernel (81 patches, machine config `SWEET`) is the
starting point because both devices share the same SoC. The port needs:

- [x] Hardware discovery from the stock ROM (`hw/HARDWARE_MAP.md`)
- [x] Firmware + DTBO extraction tooling (`tools/dtbo_scan.py`)
- [ ] Rename the machine config macro `SWEET` -> `COURBET` in the kernel
      patches (81 files) so the kernel build is courbet-specific
- [ ] Rewrite patch 0082 to drive the **Himax HX83112** touch controller
      on QUPv3 SE1 (I2C 0x48, GPIO 88/89, PM6150 LDO10 + PM6150L LDO7)
      instead of the Goodix GT9896 on sweet
- [ ] Confirm the splash framebuffer base address on courbet
      (sweet uses `0x9c000000`; courbet's ABL may differ)
- [ ] Build the kernel via GitHub Actions and boot on device

## Layout

```
src/                  <- kernel patch series (81 patches, SWEET macro)
tools/                <- host-side build / discovery tooling
hw/HARDWARE_MAP.md    <- sweet vs courbet hardware diff
hw/firmware/          <- (gitignored) extracted stock ROM artifacts
xnu/patches/          <- (gitignored) kernel source tree + patches
```

## Quick start

1. Read `docs/HARDWARE_MAP.md` for the hardware diff.
2. Run `tools/dtbo_scan.py` against a `dtbo.img` to re-extract the DTBOs.
3. See `README-courbet.md` (in the parent sweet repo, or in this
   working tree) for the full build/boot guide.
