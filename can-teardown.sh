#!/bin/sh
IFACE=can0

echo "Tearing down $IFACE"

sudo ip link set "$IFACE" down 2>/dev/null || true
sudo pkill -f "slcand.*$IFACE" 2>/dev/null || true

echo "$IFACE torn down"