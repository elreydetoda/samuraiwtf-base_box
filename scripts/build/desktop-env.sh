#!/usr/bin/env bash

set -exuo pipefail

sudo apt-get update

sudo apt-get -y install aufs-tools cgroupfs-mount mate-desktop-environment lightdm

reboot