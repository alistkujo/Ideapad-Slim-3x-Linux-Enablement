# Downloads and provenance

**Reference date: 21 October 2026.** This kit documents Linux hardware enablement for Lenovo IdeaPad Slim 3 15Q8X10 / 83N3. It is an enablement kit and configuration snapshot, not a complete operating-system installer or disk image.

The links below were checked during collection. “Page verified” means the source page loaded; “HEAD 200” means the server accepted a header-only request. Neither proves a downloaded archive's contents or signature. No multi-gigabyte media were downloaded for this kit. Links and branch contents can change.

## Installation media

| Item | Primary source | Collection status |
| --- | --- | --- |
| Fedora Workstation 44 ARM64 raw image, the original installation route | [Fedora Workstation downloads](https://fedoraproject.org/workstation/download/) | Page verified; select ARM aarch64 **Raw**, not x86_64. The original file is not included. |
| Exact historical Fedora raw-image filename | [Fedora-Workstation-Disk-44-1.7.aarch64.raw.xz](https://download.fedoraproject.org/pub/fedora/linux/releases/44/Workstation/aarch64/images/Fedora-Workstation-Disk-44-1.7.aarch64.raw.xz) | HEAD 200 through Fedora's mirror redirect, 2,930,596,248 bytes. Not downloaded. |
| KDE alternative | [Fedora KDE downloads](https://fedoraproject.org/kde/download/) and [Fedora-KDE-Desktop-Disk-44-1.7.aarch64.raw.xz](https://download.fedoraproject.org/pub/fedora/linux/releases/44/KDE/aarch64/images/Fedora-KDE-Desktop-Disk-44-1.7.aarch64.raw.xz) | Page verified; raw image HEAD 200, 3,650,564,156 bytes. This is an alternative, not the original Workstation image. |
| Ubuntu Snapdragon bootstrap media | [Ubuntu Concept announcement](https://discourse.ubuntu.com/t/ubuntu-concept-snapdragon-x-elite/48800/1), [Concept image directory](https://people.canonical.com/~platform/images/ubuntu-concept/), [Snapdragon FAQ](https://discourse.ubuntu.com/t/faq-ubuntu-25-04-25-10-on-snapdragon-x-elite/61016) | Pages verified. The directory and the announcement's Questing ARM64 image accepted HEAD requests. These rolling concept images are not verified copies of this computer's original installer. |
| Ubuntu Concept packages | [ubuntu-concept/x1e PPA](https://launchpad.net/~ubuntu-concept/+archive/ubuntu/x1e) and [package archive](https://ppa.launchpadcontent.net/ubuntu-concept/x1e/ubuntu/) | PPA address corroborated by Ubuntu's FAQ and local setup history; package archive index verified. Launchpad's descriptive page was restricted to the browsing tool. |

The user's historical setup describes Ubuntu 26.04.1 LTS with the Concept X1E packages. The exact original Ubuntu ARM64 installer filename/build and checksum were not recovered. The [general Ubuntu 26.04.1 release page](https://releases.ubuntu.com/26.04.1/) was checked but presents AMD64 media; do not use those images for this ARM laptop.

Use the signed checksum files linked by Fedora's download pages for the image you actually download. Inspect that image's partition table before extracting partitions: old sector offsets do not transfer safely to another build. The original system was installed from Workstation and subsequently switched to KDE.

## Device-tree source and patches

The local trackpad source checkout identifies:

```text
Repository: https://github.com/jglathe/linux_ms_dev_kit.git
Commit:     33237cf547a09d09d815d0cb81bf0fb560c95883
Branch recorded in the hardware report:
            jg/ubuntu-qcom-x1e-oldconfig-7.1.y
Source:     arch/arm64/boot/dts/qcom/x126100-lenovo-ideapad-slim3.dts
```

The [commit-pinned upstream DTS](https://raw.githubusercontent.com/jglathe/linux_ms_dev_kit/33237cf547a09d09d815d0cb81bf0fb560c95883/arch/arm64/boot/dts/qcom/x126100-lenovo-ideapad-slim3.dts) loaded during verification. Its header identifies BSD-3-Clause licensing. The kit preserves the minimal touchpad patch, hardware report and relevant source material; it does not duplicate the complete upstream kernel Git history. A source rebuild requires the matching full tree, included DTS/DTSI dependencies and build tools. The small patch alone is not a standalone DTB source tree.

The speaker wiring reference is [polkorny's Slim 3 DTS](https://raw.githubusercontent.com/polkorny/linux_ms_dev_kit/jg/ubuntu-qcom-x1e-7.2rc/arch/arm64/boot/dts/qcom/x126100-lenovo-ideapad-slim3.dts), verified readable with a BSD-3-Clause header. That branch link is movable; the captured local audio DTB, builder and validation report preserve the change actually prepared for this computer. Do not replace the combined working DTB wholesale with this reference file: the local DTB also contains the separately validated touchpad and USB2 changes.

The [ALSA UCM pull request 879](https://github.com/alsa-project/alsa-ucm-conf/pull/879) is an investigated audio reference, not proof that its contents were installed. The collected ALSA configuration and topology files show what this machine actually uses.

## Qualcomm and Lenovo firmware

The [qcom-firmware-updater project](https://github.com/alejandroqh/qcom-firmware-updater) loaded during verification. It extracts graphics/display/video firmware from Qualcomm's Windows driver package. Its README identifies an MIT license for the extractor and documents the historical package used here:

```text
Windows_Graphics_Driver.Core.260523131.0.152.1.Windows-ARM64.zip
Driver version: 31.0.152.1
```

Use [Qualcomm Software Center's Windows Graphics Driver page](https://softwarecenter.qualcomm.com/catalog/item/Windows_Graphics_Driver) to obtain packages from the vendor. The original ZIP is not included in this kit. The extractor's README supplies a version-specific API URL, but a header-only request to that exact historical API URL returned HTTP 403 during collection. Download access and future availability are not guaranteed. Fedora uses `dracut`; the extractor's documented `update-initramfs` step does not replace the captured Fedora-specific builder.

The [official Lenovo 83N3 Drivers and Software page](https://pcsupport.lenovo.com/us/en/products/laptops-and-netbooks/ideapad-s-series-netbooks/ideapad-slim-3-15q8x10/83n3/downloads/) loaded during verification. Select the exact model/Windows ARM64 packages there. This is a verified support landing page, not a claim that a particular historical DSP driver archive remains available.

The machine-specific GPU/display and ADSP/CDSP files in `hardware/firmware/` were copied from the working Linux installation, with firmware symlinks resolved into actual file contents. The DSP enablement history identifies the laptop's Windows DriverStore as the source of `qcadsp8380.mbn`, `qccdsp8380.mbn`, DSP DTB ELF files and service JSON files. The original Windows driver installers and their licenses were not recovered as a complete distribution package.

### Firmware licensing

Stock Fedora license material is retained under `licenses/fedora/`, including the Qualcomm and linux-firmware notices. Those notices apply according to their own file/package coverage. They do **not** automatically license separately extracted Windows firmware. The extractor's MIT license also does not grant rights to redistribute Qualcomm or Lenovo firmware. Redistribution permission for every Windows-derived blob in this kit has not been established; retain the provenance and check the vendor terms before publishing a public mirror.

## Kernel and package provenance

The running kernel and matching installed RPM family are:

```text
kernel / kernel-core / kernel-modules / kernel-modules-core
7.2.11-200.fc44.aarch64

dracut:        108-8.fc44.aarch64
qcom-firmware: 20260916-1.fc44.noarch
linux-firmware:20260916-1.fc44.noarch
```

These versions were read from the local RPM database. Personal boot snapshots, initramfs images and full installed-package inventories are excluded. Obtain matching kernel RPMs from Fedora; availability of this exact historical version is not guaranteed.

[Fedora's official kernel package source](https://src.fedoraproject.org/rpms/kernel) and [Koji build system](https://koji.fedoraproject.org/koji/) are routes for researching matching source/build packages. Their ability to supply this exact version was not verified during collection. Do not assume that the newest available kernel has been boot-tested with this kit.

