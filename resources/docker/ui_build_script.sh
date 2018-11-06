#!/usr/bin/env bash

set -e

# Update node
cd /opt/ui
npm install

# Run relay
npm run relay

# Run build
npm run build

