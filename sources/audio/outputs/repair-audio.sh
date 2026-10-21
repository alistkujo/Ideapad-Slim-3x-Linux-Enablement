#!/usr/bin/env bash
# Restore the missing topology name on this Lenovo 83N3 only.
# Uses the already-installed, distribution-provided topology; downloads nothing.
set -euo pipefail

if (( EUID != 0 )); then
    exec sudo -- /usr/bin/bash "$(readlink -f -- "$0")"
fi

family=$(cat /sys/class/dmi/id/product_family)
product=$(cat /sys/class/dmi/id/product_name)
model=$(tr -d '\000' < /sys/firmware/devicetree/base/sound/model)
if [[ "$family" != 'IdeaPad Slim 3 15Q8X10' || "$product" != '83N3' || "$model" != 'X1E80100-LENOVO-Ideapad-3' ]]; then
    printf 'Stopped: this repair is only for the inspected Lenovo Slim 3 83N3.\n' >&2
    exit 1
fi

firmware_dir=/usr/lib/firmware/qcom/x1e80100
source_file="$firmware_dir/X1E80100-Romulus-tplg.bin.xz"
alias_file="$firmware_dir/X1E80100-LENOVO-Ideapad-3-tplg.bin.xz"
expected=aa303397750f883ecaeed874d7547da658500596247676a6d405bf1ec43290b5
actual=$(xz -dc -- "$source_file" | sha256sum)
if [[ "${actual%% *}" != "$expected" ]]; then
    printf 'Stopped: the installed audio topology differs from the inspected version.\n' >&2
    exit 1
fi

if [[ -e "${alias_file%.xz}" || -L "${alias_file%.xz}" ]]; then
    printf 'Stopped: an uncompressed Slim 3 topology already exists; leaving it untouched.\n' >&2
    exit 1
fi
if [[ -e "$alias_file" || -L "$alias_file" ]]; then
    if [[ ! -L "$alias_file" || "$(readlink -- "$alias_file")" != 'X1E80100-Romulus-tplg.bin.xz' ]]; then
        printf 'Stopped: a different Slim 3 topology already exists; leaving it untouched.\n' >&2
        exit 1
    fi
else
    ln -s -- X1E80100-Romulus-tplg.bin.xz "$alias_file"
    printf 'Installed the missing audio topology alias.\n'
fi

# Retry only the failed sound-card driver. Leave the running DSPs and boot files alone.
if [[ ! -L /sys/bus/platform/devices/sound/driver ]]; then
    if ! printf '%s' sound > /sys/bus/platform/drivers/snd-x1e80100/bind; then
        printf '\nThe topology alias is installed, but the sound card did not bind.\n'
        journalctl -b -k --no-pager -n 50
        exit 1
    fi
fi
udevadm settle --timeout=15 || true
printf '\nDetected sound cards:\n'
cat /proc/asound/cards
printf '\nPlayback devices:\n'
aplay -l
printf '\nSpeaker connections:\n'
for speaker in /sys/bus/soundwire/devices/sdw:1:0:0217:0204:00:*/status; do
    [[ -e "$speaker" ]] || continue
    printf '%s: ' "$speaker"
    cat "$speaker"
done
printf '\nSystem-file repair finished. Return to the chat for speaker routing and playback checks.\n'
