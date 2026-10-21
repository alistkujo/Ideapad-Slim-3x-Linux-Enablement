# Kernel and hardware helpers

- `83n3-build-initramfs KERNEL_VERSION [OUTPUT]`: stages all machine firmware as actual files, builds a Fedora dracut initramfs, checks four critical payload names. Build to a candidate filename first.
- `83n3-status`: read-only overview of USB2/fingerprint enumeration, DSPs, battery and GPU firmware.
- `check-83n3-fingerprint`: diagnostic USB2/Goodix report; some read-only diagnostics request sudo.
- `83n3-safe-kernel-update`: update helper for the specific Fedora-through-Ubuntu-GRUB architecture. It expects the stable IDs and DTB paths shown in the guide, separate Fedora /boot, and Btrfs subvolume root. It can run DNF, mount Ubuntu read-write, edit boot entries and optionally reboot. Review these assumptions before installation.

The updater no longer embeds the original laptop's Ubuntu UUID. Supply the destination's UUID explicitly:

```bash
sudo env UBUNTU_UUID=<DESTINATION_UBUNTU_UUID> 83n3-safe-kernel-update --all
```

The placeholder is not a shell command to run unchanged. Use the real ext4 UUID from `lsblk -f`. `--reboot` is optional; omit it while reviewing a first update. The helper's name does not guarantee automatic rollback. These scripts were syntax checked; the sanitised kit has not undergone a full kernel upgrade and reboot on a second machine.

Install reviewed helpers with `sudo install -m 0755 scripts/HELPER /usr/local/bin/HELPER`. Original desktop installers, private menu backups and personal command files are excluded from this repository kit; their originals were not changed.
