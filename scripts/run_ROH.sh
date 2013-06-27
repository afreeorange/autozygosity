#!/bin/bash

SCRIPT_RANDOM=$(openssl rand -base64 12)

echo -e "Starting $SCRIPT_RANDOM"

sleep 3

echo -e "Stopping $SCRIPT_RANDOM"

