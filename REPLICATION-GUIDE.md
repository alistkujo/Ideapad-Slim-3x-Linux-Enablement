# Setup guide

These fixes target **Lenovo 83N3 / IdeaPad Slim 3 15Q8X10**. Confirm the destination model and keep recovery media and backups before changing its installation.

## 1. Install the base systems

See [download sources](DOWNLOADS-AND-PROVENANCE.md). The recorded route used Ubuntu Concept X1E packages as a bootstrap, then Fedora Workstation ARM64 raw media followed by KDE. Retain Ubuntu as a recovery environment and bootloader. Inspect the actual image partition table and destination disk identities; do not reuse another machine's NVMe numbering or partition offsets. Installing to a whole disk can overwrite existing systems.

The historical Fedora version was 44, with kernel `7.2.11-200.fc44.aarch64` used for the latest recorded setup. Install kernel packages and their matching modules consistently; this kit does not include a root filesystem, personal initramfs or installed kernel snapshots. Use destination UUIDs and the actual Btrfs subvolume in fstab and boot configuration. The original setup had Secure Boot disabled; this kit does not establish Secure Boot compatibility.

## 2. Install hardware firmware

The custom machine directory contains 22 files:

```text
hardware/firmware/usr/lib/firmware/qcom/x1p42100/LENOVO/83N3/
```

Preserve existing destination files, then copy that directory to the corresponding `/usr/lib/firmware/` path on the intended Fedora root. Install distribution `qcom-firmware` and `atheros-firmware` packages for supporting GPU/Wi-Fi firmware; relevant reference files are included. Restore SELinux labels on copied files with `restorecon` where applicable. The firmware builder verifies four critical names; all 22 machine files are still needed.

Audio also needs the Slim3 topology name under `qcom/x1e80100/`. The captured alias and Romulus target contain the same bytes. Prefer recreating the relative alias documented in `sources/audio/outputs/repair-audio.sh` after checking the target version. Use the distribution ALSA UCM package; no personal mixer state is supplied.

## 3. Select the combined DTB

The active candidate is:

```text
hardware/device-trees/fedora/active/ideapad-slim3-fixed.dtb
```

It contains the ELAN touchpad at I2C0x15/GPIO19, USB2 fix for controller a800000/Goodix27c6:650a, and audio GPIO68 plus speaker powerdown GPIO204/205 corrections. The trackpad source controller is `&i2c19`. Do not layer historical test variants on top of this binary.

Back up an existing destination DTB and install this file as `/boot/ideapad-slim3-fixed.dtb` on the intended Fedora boot filesystem. The known-good copy is identical. These repository copies have had original boot metadata removed; the hardware changes are preserved, but a new boot test is required.

## 4. Build a destination initramfs

Review `scripts/83n3-build-initramfs` and `configuration/83n3-firmware.conf`. Install the firmware before generating initramfs. Install the reviewed builder with:

```bash
sudo install -m 0755 scripts/83n3-build-initramfs /usr/local/bin/83n3-build-initramfs
```

Invoke it with the destination's exact installed kernel version and a candidate output filename. It stages dereferenced firmware, calls dracut and checks the critical payloads with lsinitrd. Keep the previous working image; promote the candidate only after verifying its contents. A copied host initramfs is not a portable installer.

## 5. Configure Ubuntu GRUB

Adapt `configuration/fedora-grub-entry.example`: replace the Fedora boot UUID, root UUID and kernel version. Paths in the entry are relative to the separate Fedora boot filesystem. `rootflags=subvol=root` assumes that Btrfs layout. The hardware arguments are retained in the template; do not substitute a private machine's command line.

Create a dedicated persistent entry in the destination Ubuntu GRUB source configuration. Regenerate and validate GRUB from Ubuntu, preserving existing Ubuntu/Windows entries. Verify every referenced kernel/initramfs/DTB exists. Provide a recovery entry pointing to real retained files. Never replace an entire machine's generated grub.cfg with someone else's snapshot.

## 6. Validate and maintain

Run `bash scripts/83n3-status` and check kernel version/command line, touchpad movement, GPU, battery, DSP state, Goodix enumeration, Wi-Fi and Bluetooth. Separately test audio channels, microphone, camera and suspend/resume. Fingerprint enrollment must use the destination user's own data and supported fprintd/authselect configuration.

See [helper instructions](scripts/README.md) before installing the updater. It requires `UBUNTU_UUID` explicitly, a separate Fedora boot filesystem, stable entry IDs/links and the documented Ubuntu-owned GRUB architecture. It can modify boot files and run DNF; its name does not imply automatic rollback. Keep a real previous kernel/module/initramfs set and test each new kernel.

## Validation and AI assistance

DTB structural comparisons verify that sanitisation changed only selected `/chosen` properties. Shell syntax and repository checksums were checked; neither proves bootability. AI assisted repairs and documentation. Review assumptions and validate on the destination laptop.
