#!/bin/sh
set -e

IFACE=can0
BITRATE=1000000

# Build list of candidate devices, filtering out unmatched globals (udev moment)
# Though most distros w/ modern Linux kernels use ttyACM,
# some of us aren't that luxurious, so we want to check ttyUSB also.
set --
for d in /dev/ttyACM* /dev/ttyUSB*; do
    [ -e "$d" ] && set -- "$@" "$d"
done

# Nothing was found
if [ "$#" -eq 0 ]; then
    echo "No /dev/ttyACM* or /dev/ttyUSB* devices found. Is the adapter plugged in?"
    exit 1
fi

# Found only one device
if [ "$#" -eq 1 ]; then
    DEV="$1"
    echo "Found one candidate device: $DEV"

# Found multiple devices
else
    echo "Multiple serial devices found:"
    i=1
    for d in "$@"; do
        INFO=$(udevadm info -q property -n "$d" 2>/dev/null | grep -E 'ID_VENDOR=|ID_MODEL=|ID_SERIAL_SHORT=' | tr '\n' ' ' || true)
        echo "  $i) $d   $INFO"
        i=$((i + 1))
    done

    printf "Select device number: "
    read -r SELECTION

    eval "DEV=\${$SELECTION}"

    if [ -z "$DEV" ]; then
        echo "Invalid selection. Try again"
        exit 1
    fi
fi

# Clean up any zombie instance first
sudo ip link set "$IFACE" down 2>/dev/null || true
sudo pkill -f "slcand.*$IFACE" 2>/dev/null || true
sleep 0.2

echo "Setting up $IFACE on $DEV"
sudo slcand -o -c -s8 "$DEV" "$IFACE"
sleep 0.2

sudo ip link set "$IFACE" type can bitrate "$BITRATE"
sudo ip link set "$IFACE" up

echo "$IFACE is up on $DEV"