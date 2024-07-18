#!/bin/bash

# this script does not work

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Start OpenVPN with loaded credentials
sudo -b openvpn --config "$VPN_CONFIG_FILE" --auth-user-pass <(echo -e "${VPN_USERNAME}\n${VPN_PASSWORD}")