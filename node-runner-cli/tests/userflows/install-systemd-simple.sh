#!/bin/bash
#set -x
set -e
# enable thos in case you want to execute this locally or on a fresh node.
export KEYSTORE_PASSWORD=radix
export POSTGRES_PASSWORD=radix
export NGINX_ADMIN_PASSWORD=radix
export NGINX_METRICS_PASSWORD=radix
export NGINX_GATEWAY_PASSWORD=radix
export SEED_NODE=radix://node_tdx_e_1q0gm3fwqh8ggl09g7l8ru96krzlxdyrc694mqw8cf227v62vjyrmccv8md5@13.126.65.118,radix://node_tdx_e_1q0juzf2gnhfhy2aj6x88x4f459tf2a2mdk56jm3ffhzp94fn8k0q5lkse34@52.64.209.45,radix://node_tdx_e_1qdzlwtjn9wcmcyt3mp3g4qaerr6fgrl86ze6t20427tf4rmnu670y0cgszc@54.72.0.65,radix://node_tdx_e_1qfz9r8xp95vuzjq503l856ywukrdnukcz4232tr4nsx7ff2efvfnwvaq080@35.168.132.18
export NETWORK_ID=14
export NETWORK_NAME=zabanet

export DISABLE_VERSION_CHECK=true
export COMPOSE_HTTP_TIMEOUT=360
#Below PATH require when ansible is installed as part of pip
export PATH="$PATH:/home/ubuntu/.local/bin"

./babylonnode systemd stop && sudo rm -rf $HOME/babylon-ledger | true

./babylonnode systemd config -m CORE \
  -n ${NETWORK_ID} \
  -t ${SEED_NODE} \
  -i 13.126.65.118 \
  -v "not_a_real_validator_address" \
  -k $KEYSTORE_PASSWORD -nk \
  -dd $HOME/babylon-ledger \
  -a

./babylonnode systemd install -a

./babylonnode auth set-admin-password --setupmode SYSTEMD -p $NGINX_ADMIN_PASSWORD
./babylonnode auth set-superadmin-password --setupmode SYSTEMD -p $NGINX_SUPERADMIN_PASSWORD
./babylonnode auth set-metrics-password --setupmode SYSTEMD -p $NGINX_METRICS_PASSWORD

NGINX_ADMIN_PASSWORD=$NGINX_ADMIN_PASSWORD ./babylonnode api system health
NGINX_ADMIN_PASSWORD=$NGINX_ADMIN_PASSWORD ./babylonnode api system version
$NGINX_METRICS_PASSWORD=$NGINX_METRICS_PASSWORD ./babylonnode api system metrics
#TODO: add command against metrics endpoint

./babylonnode systemd stop