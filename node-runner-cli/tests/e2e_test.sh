#!/bin/bash

radixnode systemd config -a -t "somenode" -i "1.1.1.1" -k "password" -n S -dd "/tmp/babylon-ledger"
radixnode systemd install -a