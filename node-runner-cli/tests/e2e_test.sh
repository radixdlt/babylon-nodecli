#!/bin/bash

radixnode systemd config -a true -t "somenode" -i "1.1.1.1" -kp "password" -n S -dd "/tmp/data"
radixnode systemd install -a true