# Hardware sources

`trackpad/` contains the clean and expanded ELAN patches, measured GPIO19 hardware report, standalone node, pristine/modified machine DTS and repository provenance. The actual source controller is `&i2c19`; an older narrative's `&i2c0` example was incorrect. The pinned source commit and repository are recorded in `trackpad/machine-dts/PROVENANCE.json`. Rebuilding that source requires its matching full kernel tree and DTSI dependencies.

`audio/outputs/repair-audio.sh` documents the Slim3-to-Romulus topology alias and verifies its source before binding the sound card. `audio/work/prepare_audio_dtb.py` applies and validates the audio-only wiring changes on the captured pre-audio DTB. Its default input and expected hash were adapted to the sanitised historical DTB; an optional first argument selects another input. It writes project outputs, not installed boot files. It requires dtc/fdtput. This builder is a provenance/rebuild tool, not a boot installer.

`decompiled-device-trees/` contains standalone readable versions of the sanitised hardware DTBs. `SANITIZATION.json` records the properties removed from each binary. No hardware nodes or properties were changed by sanitisation. Bootloader-generated /chosen arguments, UEFI pointers, seeds and initrd addresses were removed because they belong to a particular boot/session. GRUB must supply destination kernel arguments at boot. The rebuilt/sanitised binaries have different hashes from the original tested copies and have not been reboot-tested in this form.

Upstream author copyright and licence notices remain intact. AI assisted the collection and some original repairs; review and test hardware changes before use.
