# Lenovo 83N3 Linux enablement

Device trees, firmware, source patches and kernel helpers for **Lenovo IdeaPad Slim 3 15Q8X10 / 83N3**, Qualcomm Snapdragon X / ARM64. The documented installation uses Fedora with Ubuntu providing GRUB.

This repository kit contains hardware enablement work, without personal themes, wallpapers, login settings, account inventories or machine boot snapshots. The original system and personal source folders were not changed.

## Contents

| Path | Contents |
|---|---|
| `hardware/device-trees/fedora/active/` | Combined trackpad, USB2/fingerprint and audio DTB; matching known-good copy |
| `hardware/device-trees/` | Earlier hardware variants, clearly separated from the active variant |
| `hardware/firmware/` | 22 machine-specific payloads plus relevant GPU, Wi-Fi, Bluetooth and audio topology files |
| `sources/` | Trackpad patches, measured hardware report, pinned source provenance, audio builder and readable DTBs |
| `scripts/` | Initramfs builder, diagnostics and configurable kernel updater |
| `configuration/` | Dracut firmware configuration and a GRUB entry template |
| `licenses/` | Captured stock package/firmware notices |

Read [the setup guide](REPLICATION-GUIDE.md), [download sources](DOWNLOADS-AND-PROVENANCE.md) and [helper instructions](scripts/README.md). Verify integrity with `python3 VERIFY.py`.

## Portability and validation

The model-specific hardware settings are retained. Personal disk UUIDs and bootloader-generated `/chosen` data were removed from the supplied DTBs. Hardware nodes/properties and memory reservations were compared before and after sanitisation and are unchanged. Sanitised DTBs have new hashes and have not been reboot-tested in this form; supply destination boot arguments through GRUB. Details are in [SANITIZATION.json](SANITIZATION.json).

The updater requires the destination Ubuntu UUID through `UBUNTU_UUID`; no personal disk identifier is embedded. It remains specific to the documented Fedora/Ubuntu boot architecture. Review its assumptions before running it.

The original installation reported a working touchpad, fingerprint detection, DSPs, GPU and battery. These historical results do not certify every function on a second laptop. Speaker playback/stereo, camera, microphone and suspend require destination testing.

Base OS media and matching kernel packages must be downloaded separately. Windows-derived firmware permissions have not been established for public redistribution; stock notices and the extractor licence do not automatically cover those blobs. See download/provenance notes before publishing firmware.

## AI assistance

AI assisted some original repairs, scripts and documentation. Review the source and target paths; this kit has not been validated through a fresh installation on another laptop.
