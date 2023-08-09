#!/bin/bash

babylonnode systemd config -a -t "somenode" -i "1.1.1.1" -k "password" -n S -dd "/tmp/babylon-ledger"
babylonnode systemd install -a