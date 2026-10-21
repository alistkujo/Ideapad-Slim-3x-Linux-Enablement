#!/usr/bin/env python3
"""Create an audio-only DTB variant and verify every node/property change.

Audio wiring reference (BSD-3-Clause):
https://github.com/polkorny/linux_ms_dev_kit/blob/jg/ubuntu-qcom-x1e-7.2rc/arch/arm64/boot/dts/qcom/x126100-lenovo-ideapad-slim3.dts
"""

import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(__import__('sys').argv[1]) if len(__import__('sys').argv) > 1 else ROOT.parent.parent / 'hardware/device-trees/fedora/historical/ideapad-slim3-fixed.dtb.before-audio-20261015-225147'
OUTPUT = ROOT / 'outputs/ideapad-slim3-audio.dtb'
REPORT = ROOT / 'work/audio-dtb-validation.json'
SOURCE_SHA256 = '562d1471a079ff9884c091b3163afa24382b240c4301d89ab3b91755b33ff0c0'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def cells(*values):
    return struct.pack('>' + 'I' * len(values), *values)


def string(value):
    return value.encode('ascii') + b'\0'


def parse(blob):
    header = struct.unpack_from('>10I', blob)
    require(header[0] == 0xD00DFEED, 'Not an FDT blob')
    require(header[1] <= len(blob), 'Truncated FDT')
    struct_off, strings_off, reserve_off = header[2:5]
    nodes = {}
    stack = []
    pos = struct_off
    while True:
        token = struct.unpack_from('>I', blob, pos)[0]
        pos += 4
        if token == 1:
            end = blob.index(b'\0', pos)
            name = blob[pos:end].decode('ascii')
            pos = (end + 4) & ~3
            stack.append(name)
            path = '/' + '/'.join(stack[1:])
            require(path not in nodes, 'Duplicate node: ' + path)
            nodes[path] = {}
        elif token == 2:
            stack.pop()
        elif token == 3:
            size, nameoff = struct.unpack_from('>2I', blob, pos)
            pos += 8
            end = blob.index(b'\0', strings_off + nameoff)
            name = blob[strings_off + nameoff:end].decode('ascii')
            path = '/' + '/'.join(stack[1:])
            require(name not in nodes[path], 'Duplicate property: ' + path + '/' + name)
            nodes[path][name] = blob[pos:pos + size]
            pos = (pos + size + 3) & ~3
        elif token == 4:
            continue
        elif token == 9:
            require(not stack, 'Unclosed nodes')
            break
        else:
            raise RuntimeError(f'Unexpected FDT token: {token}')
    reserves = []
    pos = reserve_off
    while True:
        address, size = struct.unpack_from('>2Q', blob, pos)
        pos += 16
        if address == 0 and size == 0:
            break
        reserves.append([address, size])
    return nodes, reserves, header[7]


def symbol(nodes, name):
    return nodes['/__symbols__'][name].rstrip(b'\0').decode('ascii')


def one_cell(value):
    require(len(value) == 4, 'Expected a single cell')
    return struct.unpack('>I', value)[0]


def render(value):
    if value is None:
        return None
    if not value:
        return {'boolean': True}
    if value.endswith(b'\0') and all(32 <= c <= 126 or c == 0 for c in value):
        return {'strings': value[:-1].decode('ascii').split('\0')}
    if len(value) % 4 == 0:
        return {'cells_hex': [hex(v) for v in struct.unpack('>' + 'I' * (len(value) // 4), value)]}
    return {'bytes_hex': value.hex()}


def main():
    source_blob = SOURCE.read_bytes()
    require(hashlib.sha256(source_blob).hexdigest() == SOURCE_SHA256,
            'Source DTB changed; inspect it again before preparing a patch')
    before, reserves_before, boot_cpu_before = parse(source_blob)
    tlmm = symbol(before, 'tlmm')
    swr = symbol(before, 'swr0')
    left = symbol(before, 'left_spkr')
    right = symbol(before, 'right_spkr')
    wsa_pin = symbol(before, 'wsa_swr_active')
    old_pin = symbol(before, 'spkr_01_sd_n_active')
    tlmm_handle = one_cell(before[tlmm]['phandle'])
    wsa_handle = one_cell(before[wsa_pin]['phandle'])
    old_handle = one_cell(before[old_pin]['phandle'])
    require(before[swr]['pinctrl-0'] == cells(wsa_handle, old_handle),
            'Unexpected existing SoundWire pinctrl configuration')
    require(before[left]['reset-gpios'] == before[right]['reset-gpios'],
            'Speaker resets differ from the inspected source')
    require(before[left]['reset-gpios'] == cells(
        one_cell(before[symbol(before, 'lpass_tlmm')]['phandle']), 12, 1),
        'Unexpected existing speaker reset')
    require(before[left]['reg'] == cells(0, 0) and before[right]['reg'] == cells(0, 1),
            'Unexpected speaker addresses')
    max_handle = max(one_cell(value) for props in before.values()
                     for name, value in props.items()
                     if name in ('phandle', 'linux,phandle'))
    new_handles = [max_handle + offset for offset in (1, 2, 3)]
    require(new_handles[-1] < 0xFFFFFFFF, 'No free phandles')
    pin_paths = [tlmm + '/' + name for name in (
        'spkr-en1-default-state', 'spkr-en2-default-state', 'audio-en-default-state')]
    regulator = '/regulator-audio-en'
    expected_new = {}
    for path, gpio, handle in zip(pin_paths, (204, 205, 68), new_handles):
        expected_new[path] = {
            'pins': string(f'gpio{gpio}'),
            'function': string('gpio'),
            'drive-strength': cells(2),
            'bias-disable': b'',
            'phandle': cells(handle),
        }
    expected_new[regulator] = {
        'compatible': string('regulator-fixed'),
        'regulator-name': string('VREG_AUDIO_EN'),
        'gpio': cells(tlmm_handle, 68, 0),
        'enable-active-high': b'',
        'pinctrl-0': cells(new_handles[2]),
        'pinctrl-names': string('default'),
        'regulator-always-on': b'',
        'regulator-boot-on': b'',
    }
    require(not set(expected_new).intersection(before), 'One of the new nodes already exists')
    expected_changes = {
        (swr, 'pinctrl-0'): cells(wsa_handle, *new_handles[:2]),
        (left, 'reset-gpios'): None,
        (right, 'reset-gpios'): None,
        (left, 'powerdown-gpios'): cells(tlmm_handle, 204, 1),
        (right, 'powerdown-gpios'): cells(tlmm_handle, 205, 1),
    }
    for path, props in expected_new.items():
        for name, value in props.items():
            expected_changes[path, name] = value
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='audio-dtb-', dir=ROOT / 'work') as temp:
        candidate = Path(temp) / 'candidate.dtb'
        shutil.copyfile(SOURCE, candidate)
        for path in expected_new:
            subprocess.run(['fdtput', '-c', str(candidate), path], check=True)
        for (path, name), value in expected_changes.items():
            if value is None:
                command = ['fdtput', '-d', str(candidate), path, name]
            else:
                command = ['fdtput', '-t', 'bx', str(candidate), path, name]
                command.extend(f'{byte:02x}' for byte in value)
            subprocess.run(command, check=True)
        output_blob = candidate.read_bytes()
        after, reserves_after, boot_cpu_after = parse(output_blob)
        require(set(after) - set(before) == set(expected_new), 'Unexpected new nodes')
        require(not set(before) - set(after), 'Existing nodes removed')
        actual_changes = {}
        report_changes = []
        for path in sorted(set(before) | set(after)):
            old_props = before.get(path, {})
            new_props = after.get(path, {})
            for name in sorted(set(old_props) | set(new_props)):
                old, new = old_props.get(name), new_props.get(name)
                if old != new:
                    actual_changes[path, name] = new
                    report_changes.append({
                        'node': path, 'property': name,
                        'before': render(old), 'after': render(new),
                    })
        require(actual_changes == expected_changes, 'Property diff exceeds the intended audio patch')
        require(reserves_before == reserves_after, 'Memory reservations changed')
        require(boot_cpu_before == boot_cpu_after, 'Boot CPU changed')
        # Compile the complete result as a structural check; diagnostics are retained.
        checked = subprocess.run(['dtc', '-I', 'dtb', '-O', 'dtb', '-o', '/dev/null', str(candidate)],
                                 capture_output=True, text=True)
        require(checked.returncode == 0, 'DTB structural check failed: ' + checked.stderr)
        OUTPUT.write_bytes(output_blob)
    require(SOURCE.read_bytes() == source_blob, 'Source changed during preparation')
    report = {
        'source': str(SOURCE), 'source_sha256': SOURCE_SHA256,
        'output': str(OUTPUT), 'output_sha256': hashlib.sha256(output_blob).hexdigest(),
        'source_size': len(source_blob), 'output_size': len(output_blob),
        'source_nodes': len(before), 'output_nodes': len(after),
        'new_nodes': sorted(expected_new), 'changed_properties': report_changes,
        'existing_property_changes': 5,
        'all_other_properties_identical': True,
        'memory_reservations_identical': True,
        'boot_cpu_identical': True,
        'new_phandles': [hex(v) for v in new_handles],
        'dtc_exit_code': checked.returncode,
        'dtc_warnings': checked.stderr,
        'reference': 'https://github.com/polkorny/linux_ms_dev_kit/blob/jg/ubuntu-qcom-x1e-7.2rc/arch/arm64/boot/dts/qcom/x126100-lenovo-ideapad-slim3.dts',
    }
    REPORT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items()
                      if key not in ('changed_properties', 'dtc_warnings')}, indent=2))
    print(f'Validated {len(actual_changes)} property changes; all other properties match exactly.')


if __name__ == '__main__':
    main()
