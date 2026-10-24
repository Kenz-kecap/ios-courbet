# ios-courbet: iOS 16 on Xiaomi Mi 11 Lite 4G (courbet, SM7150)

Port of dipa-studio/ios-sweet (Redmi Note 10 Pro / "sweet") to the
Xiaomi Mi 11 Lite 4G (codename "courbet", M2101K9AG, Qualcomm SM7150 /
Snapdragon 732G). Both devices share the same SoC (SM7150: 6x A55 +
2x A76 Kryo 470, GICv3, UFS, PM6150+PM6150L), so the XNU kernel patch
series (0001-0081) is reused **as-is** — the only differences are in
board-specific hardware addresses, framebuffer location, touch
controller, and the device-tree that the kernel consumes.

## What we keep from sweet
- XNU kernel build pipeline (`.github/workflows/xnu.yml`, all 81
  patches in `xnu/patches/`). The machine config macro is still
  `SWEET` (kernel build flag), but the board it targets is now courbet.
  We keep the `SWEET` name to avoid a full kernel rebuild on every
  trivial change.
- Shim loader architecture (`shim/`), UFS takeover, HFS+ root layout,
  iOS 16.7.16 (iPhone X / D22AP) userland, activation path, etc.

## What changes for courbet
- **Framebuffer (splash)**: ABL's contiguous-splash region on courbet
  is at a *different* physical address than sweet's 0x9c000000. We
  discover it by reading the live FDT `/reserved-memory` from the
  stock `boot.img` and expose it through `shim/console.h` +
  `shim/mmu.h` + `tools/mkadt.py`.
- **Touch controller**: sweet used Goodix GT9896 on GENI SE7 I2C
  (`0xa84000`). Courbet uses **Himax HX83xx (`himax,hxcommon`) at
  I2C 0x48** on QUPv3 SE1 I2C (`qupv3_se1_i2c`, target =
  `qupv3_se5_i2c` in vendor overlay), with IRQ on TLMM GPIO 89 and
  RESET on GPIO 88. The existing kernel patch 0063 is Goodix-specific
  register packing, so we need a new patch (`0082-courbet-himax-touch`)
  that drives the Himax protocol (different command register map and
  report format) over the same GENI I2C FIFO engine.
- **Power/volume keys**: same PM6150 PON via SPMI as sweet (chip is
  identical). GPIO mapping for vol-up is PM6150L GPIO2 (SID 4, same as
  sweet). No change needed in the SPMI observer code.
- **Battery**: same IOPMPowerSource static service, no change.
- **UFS**: same `qcom,ufshc` base address `0x01d84000` on SM7150.
  No change.
- **GIC / timers / CPU topology**: identical SM7150. No change.

## Hardware fact sheet (courbet)

| Component | Value | Source |
|---|---|---|
| SoC | Qualcomm SM7150 (Snapdragon 732G) | datasheet / firmware |
| CPU | 8 cores Kryo 470: 0-5 = A55 @1.8 GHz, 6-7 = A76 @2.3 GHz | boot DTS |
| GIC | GICv3 with security extensions; GICD 0x17a00000, GICR 0x17a60000 | SM7150 TRM |
| Timer | armv8-timer, PPI INTIDs: phys=2, virt=3, hyp=4, sec=1 | boot DTS |
| RAM | 6 GB LPDDR4X (or 8 GB on some variants) | spec |
| UFS host | `0x01d84000` (same as sweet) | DTBO |
| Touch | **Himax HX83112** (`himax,hxcommon`), I2C addr `0x48`, on QUPv3 SE1 | DTBO fragment@27 |
| Touch IRQ | TLMM GPIO `0x59` = 89 | DTBO |
| Touch RESET | TLMM GPIO `0x58` = 88 | DTBO |
| Touch VDD | `pm6150_l10` (PM6150 LDO10) | DTBO fixup |
| Touch AVDD | `pm6150l_l7` (PM6150L LDO7) | DTBO fixup |
| Vol+ key | PM6150L GPIO2 (SPMI SID 4) via SPMI observer | DTBO fragment@19/20 |
| Power key | PM6150 PON register 0x810 bits 1&2 | same as sweet |
| Panel | 1080x2400 AMOLED DSC, 90 Hz | spec |

## TODO / next actions

1. [ ] Extract live FDT from stock `boot.img` and confirm:
   - GICv3 GICD/GICR physical base (expected: 0x17a00000 / 0x17a60000)
   - Contiguous splash framebuffer address (sweet was 0x9c000000;
     courbet may be at a different address)
   - UFS host `reg` (expected: 0x01d84000)
2. [ ] Add `shim/courbet.h` with `COURBET_FB_BASE` etc., or parameterize
   `console.h` / `mmu.h` so the same shim binary works on both boards
   (chosen by FDT magic or compile-time macro).
3. [ ] Write kernel patch `0082-courbet-himax-touch.patch`:
   - Same GENI QUPv3 I2C FIFO engine as 0060/0063
   - New driver for the Himax HX83112 protocol
     (`touch_himax.c` / `SweetHIDHimax`)
   - IRQ handling via gpio-keys notifier (GPIO 89)
   - Reset sequence: GPIO 88 low 20 ms → high → wait for IC
4. [ ] Adapt `tools/mkadt.py`:
   - Change `FB` to the discovered courbet splash address
   - Add `/arm-io/touch0` node for the Himax controller (or keep
     the same driver-match path and only change the I2C target)
   - Update `cpus` topology comment (same 8 cores)
5. [ ] Verify ABL's `cont_splash_region` on courbet: dump
   `/reserved-memory` from the live FDT after booting stock Android
   once (via `adb` + `cat /proc/device-tree/reserved-memory/...`).
6. [ ] Build the kernel via GitHub Actions (fork the repo, run
   `xnu.yml`), download the kernel artifact, build the shim +
   payload, and flash via `fastboot boot`.

## Layout

```
hw/
  firmware/
    miui_courbet.zip          # original 3.7 GB firmware zip
    extracted/                # unzipped (boot.img, dtbo.img, ...)
    boot_unpacked/            # stock boot.img unpacked (dtb, ramdisk)
    dtbo_dtbs/                # all 40 DTBO entries extracted (raw .dtb)
    dtbo_scan.py              # tool to re-extract DTBO entries
shim/                         # modified from ios-sweet
tools/                        # modified from ios-sweet
xnu/patches/                  # 81 patches from sweet + new 0082
```
