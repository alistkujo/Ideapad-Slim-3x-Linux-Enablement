# Lenovo IdeaPad Slim 3x 15Q8X10 / 83N3
## ELAN I2C-HID touchpad hardware validation

### Machine

- Lenovo IdeaPad Slim 3x 15Q8X10
- Lenovo machine type: **83N3**
- Qualcomm Snapdragon X platform
- Device-tree source:
  `arch/arm64/boot/dts/qcom/x126100-lenovo-ideapad-slim3.dts`
- Tested source branch:
  `jg/ubuntu-qcom-x1e-oldconfig-7.1.y`
- Base source commit:
  `33237cf547a09d09d815d0cb81bf0fb560c95883`

## Problem

The existing device tree describes an active I2C-HID touchpad at
address `0x5d`.

The tested 83N3 unit does not contain the touchpad at `0x5d`.

Alternative touchpad definitions existed in the source but were
commented out.

## Physical touchpad identification

A protocol-correct HID-over-I2C descriptor probe found a responding
device at:

- I2C controller: Qualcomm Geni I2C used by `&i2c19`
- Linux runtime bus during testing: bus 0
- I2C address: **0x15**
- HID descriptor register: **0x0001**

30-byte HID descriptor:

```
1e 00 00 01
a3 02
02 00
03 00
1f 00
04 00
00 00
05 00
06 00
f3 04
7e 32
04 00
00 00 00 00
```

Decoded identity:

- Vendor ID: **0x04f3 (ELAN)**
- Product ID: **0x327e**
- HID version: **0x0004**
- Maximum input length: **31 bytes**

Linux identifies the device as:

```
hid-over-i2c 04F3:327E Touchpad
```

## GPIO interrupt discovery

Initial experimental IRQ assignments were incorrect.

GPIO3 was tested and did not receive touchpad interrupts.

GPIO67 is the keyboard IRQ. Keyboard activity increased the
`msmgpio 67 Level hid-over-i2c` interrupt counter, whereas touchpad
activity did not.

A scan of stable input GPIO state while generating ELAN input reports
identified **GPIO19**.

### GPIO19 proof

With the ELAN powered, reset, and operating:

1. GPIO19 was HIGH while idle.
2. Touch/click activity caused GPIO19 to go LOW.
3. GPIO19 remained LOW after the hand was removed while reports were pending.
4. Reading the ELAN returned valid HID reports beginning `0b 00`
   (11-byte reports).
5. Once the pending reports were drained, GPIO19 returned HIGH.
6. This sequence was repeated successfully **three consecutive times**.

Observed sequence:

```
idle:
gpio19 = HIGH

touch/click:
gpio19 = LOW

ELAN reads:
0b 00 ...
0b 00 ...
00 00 ...

after draining:
gpio19 = HIGH
```

This demonstrates an active-low interrupt line consistent with:

```dts
interrupts-extended = <&tlmm 19 IRQ_TYPE_LEVEL_LOW>;
```

## HID validation

After manually issuing the HID-over-I2C POWER ON / RESET sequence,
the ELAN produced real HID input data.

Example:

```
Total reads       : 60
Valid HID reports : 43

Valid lengths:
  11 bytes : 43
```

Example reports:

```
0b 00 01 00 00 ff 00 00 00 00 00
0b 00 01 00 e2 0d 00 00 00 00 00
0b 00 01 00 43 d3 00 00 00 00 00
0b 00 01 01 00 00 00 00 00 00 00
```

## Working device-tree definition

```dts
touchpad@15 {
	compatible = "hid-over-i2c";
	reg = <0x15>;

	hid-descr-addr = <0x1>;
	interrupts-extended = <&tlmm 19 IRQ_TYPE_LEVEL_LOW>;

	vdd-supply = <&vreg_misc_3p3>;
	vddl-supply = <&vreg_l12b_1p2>;

	wakeup-source;
};
```

## Final hardware test

The device tree was changed from the incorrect touchpad definition
to:

- ELAN at **0x15**
- HID descriptor register **0x0001**
- TLMM **GPIO19**
- **IRQ_TYPE_LEVEL_LOW**

The resulting DTB was booted on the physical Lenovo 83N3.

### Result: WORKING

The touchpad works under Fedora KDE during a normal boot using the
patched DTB.

The pre-existing normal DTB and known-working patched DTB were kept
as separate backup files during testing.

## Proposed source change

Remove the active `touchpad@5d` definition and enable the
ELAN06FA `touchpad@15` definition using:

```dts
interrupts-extended = <&tlmm 19 IRQ_TYPE_LEVEL_LOW>;
```

This patch is contained in:

`0001-arm64-dts-qcom-x126100-slim3-fix-elan-touchpad.patch`
