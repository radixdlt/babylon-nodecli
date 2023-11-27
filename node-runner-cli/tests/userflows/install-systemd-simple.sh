#!/bin/bash
set -x
set -e
whoami
# enable thos in case you want to execute this locally or on a fresh node.
#export KEYSTORE_PASSWORD=radix
#export POSTGRES_PASSWORD=radix
#export NGINX_ADMIN_PASSWORD=radix
#export NGINX_METRICS_PASSWORD=radix
#export NGINX_GATEWAY_PASSWORD=radix
#export SEED_NODE=radix://node_tdx_e_1q0gm3fwqh8ggl09g7l8ru96krzlxdyrc694mqw8cf227v62vjyrmccv8md5@13.126.65.118,radix://node_tdx_e_1q0juzf2gnhfhy2aj6x88x4f459tf2a2mdk56jm3ffhzp94fn8k0q5lkse34@52.64.209.45,radix://node_tdx_e_1qdzlwtjn9wcmcyt3mp3g4qaerr6fgrl86ze6t20427tf4rmnu670y0cgszc@54.72.0.65,radix://node_tdx_e_1qfz9r8xp95vuzjq503l856ywukrdnukcz4232tr4nsx7ff2efvfnwvaq080@35.168.132.18
#export NETWORK_ID=14
#export NETWORK_NAME=zabanet

df -H
docker system df

export DISABLE_VERSION_CHECK=true
export COMPOSE_HTTP_TIMEOUT=360
#Below PATH require when ansible is installed as part of pip
export PATH="$PATH:/home/ubuntu/.local/bin"
export IP=$(curl https://api.ipify.org)

echo "Found this IP: $IP"

./babylonnode systemd stop && sudo rm -rf ${HOME}/babylon-ledger | true

./babylonnode systemd config -m CORE \
  -n ${NETWORK_ID} \
  -t ${SEED_NODE} \
  -i ${IP} \
  -v "" \
  -k ${KEYSTORE_PASSWORD} -nk \
  -dd ${HOME}/babylon-ledger \
  -a

cat ${HOME}/babylon-node-config/config.yaml

./babylonnode systemd install -a

echo "Check radixdlt service status"
sudo systemctl status radixdlt-node.service --no-pager

echo "Check nginx service status"
sudo systemctl status nginx.service --no-pager

sleep 10

echo "Checking radixdlt service status again"
sudo systemctl status radixdlt-node.service --no-pager

echo "Checking nginx service status again"
sudo systemctl status nginx.service --no-pager

echo "Set credentials"
./babylonnode auth set-admin-password --setupmode SYSTEMD -p ${NGINX_ADMIN_PASSWORD}
./babylonnode auth set-metrics-password --setupmode SYSTEMD -p ${NGINX_METRICS_PASSWORD}

echo "Testing Core node health endpoint"
set +e
for i in {1..5}; do
  FULL_OUTPUT=$(NGINX_ADMIN_PASSWORD=${NGINX_ADMIN_PASSWORD} ./babylonnode api system health)
  OUTPUT=$(echo $FULL_OUTPUT | jq -r '.status')
  if [[ $OUTPUT == "SYNCING" || $OUTPUT == "BOOTING_AT_GENESIS" || $OUTPUT == "OUT_OF_SYNC" || $OUTPUT == "BOOTING" || $OUTPUT == "UP" ]]; then
    echo "The result is successful"
    echo "The Node is in status $OUTPUT"
    break
  else
    if [[ $i == 5 ]]; then
      echo "failed to get ready in time."
      echo "here are the logs of the core node"
      journalctl -u radixdlt-node.service --no-pager --lines 100
      echo "Exiting..."
      exit 137
    fi
    echo "The result is unsuccessful. Waiting and trying again ($i of 5)"
    echo "Command ./babylonnode api system health resulted in"
    echo "$FULL_OUTPUT"
  fi
  sleep 30
done
set -e

echo "Testing Core node version endpoint"
NGINX_ADMIN_PASSWORD=${NGINX_ADMIN_PASSWORD} ./babylonnode api system version

echo "Testing Core node metrics endpoint"
NGINX_METRICS_PASSWORD=${NGINX_METRICS_PASSWORD} ./babylonnode api metrics

echo "Testing Core node network sync status"
NGINX_ADMIN_PASSWORD=${NGINX_ADMIN_PASSWORD} ./babylonnode api system network-sync-status

echo "Testing Core node configuration"
NGINX_ADMIN_PASSWORD=${NGINX_ADMIN_PASSWORD} ./babylonnode api system configuration

echo "Testing Core node peers"
NGINX_ADMIN_PASSWORD=${NGINX_ADMIN_PASSWORD} ./babylonnode api system peers

echo "Testing Core node identity"
NGINX_ADMIN_PASSWORD=${NGINX_ADMIN_PASSWORD} ./babylonnode api system identity

echo "Restarting systemd service"
./babylonnode systemd restart

echo "Stopping systemd service"
./babylonnode systemd stop

sleep 10

echo "Checking radixdlt service status again"
sudo systemctl status radixdlt-node.service --no-pager | true

echo "Checking nginx service status again"
sudo systemctl status nginx.service --no-pager| true

echo "Starting systemd service"
./babylonnode systemd start

sleep 10

echo "Checking radixdlt service status again"
sudo systemctl status radixdlt-node.service --no-pager

echo "Checking nginx service status again"
sudo systemctl status nginx.service --no-pager

echo "Stopping systemd service"
./babylonnode systemd stop

df -H
docker system df

sudo rm -rf ${HOME}/babylon-ledger/