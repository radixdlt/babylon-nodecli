#!/bin/bash
set -x
set -e
whoami

df -H
docker system df

# enable thos in case you want to execute this locally or on a fresh node.
#export KEYSTORE_PASSWORD=radix
#export POSTGRES_PASSWORD=radix
#export NGINX_ADMIN_PASSWORD=radix
#export NGINX_METRICS_PASSWORD=radix
#export NGINX_GATEWAY_PASSWORD=radix
#export SEED_NODE=radix://node_rdx1qf2x63qx4jdaxj83kkw2yytehvvmu6r2xll5gcp6c9rancmrfsgfw0vnc65@52.212.35.209,radix://node_rdx1qgxn3eeldj33kd98ha6wkjgk4k77z6xm0dv7mwnrkefknjcqsvhuu4gc609@54.79.136.139,radix://node_rdx1qwrrnhzfu99fg3yqgk3ut9vev2pdssv7hxhff80msjmmcj968487uugc0t2@43.204.226.50,radix://node_rdx1q0gnmwv0fmcp7ecq0znff7yzrt7ggwrp47sa9pssgyvrnl75tvxmvj78u7t@52.21.106.232
#export NETWORK_ID=1
#export NETWORK_NAME=mainnet

export DISABLE_VERSION_CHECK=true
export COMPOSE_HTTP_TIMEOUT=360
#Below PATH require when ansible is installed as part of pip
export PATH="$PATH:/home/ubuntu/.local/bin"

echo "set old version"
#RADIXDLT_APP_VERSION_OVERRIDE=rcnet-v3.1-r5

./babylonnode docker config -d $HOME/babylon-node-config \
  -t ${SEED_NODE} \
  -m CORE GATEWAY \
  -n ${NETWORK_ID} \
  -k ${KEYSTORE_PASSWORD} -nk \
  -p ${POSTGRES_PASSWORD} \
  -v "" \
  -a

cat $HOME/babylon-node-config/config.yaml

echo "unset version override"
unset RADIXDLT_APP_VERSION_OVERRIDE

# Reset everything
./babylonnode docker stop | true
sudo rm -rf /home/radixdlt/babylon-ledger/*
./babylonnode monitoring stop | true

# Setup passwords details
DOCKER_COMPOSE_FOLDER_PREFIX=$(whoami) ./babylonnode auth set-admin-password -m DOCKER -p ${NGINX_ADMIN_PASSWORD}
DOCKER_COMPOSE_FOLDER_PREFIX=$(whoami) ./babylonnode auth set-metrics-password -m DOCKER -p ${NGINX_METRICS_PASSWORD}
DOCKER_COMPOSE_FOLDER_PREFIX=$(whoami) ./babylonnode auth set-gateway-password -m DOCKER -p ${NGINX_GATEWAY_PASSWORD}

./babylonnode monitoring config \
  -m MONITOR_CORE MONITOR_GATEWAY \
  -cm ${NGINX_METRICS_PASSWORD} \
  -gm ${NGINX_METRICS_PASSWORD} \
  -am ${NGINX_METRICS_PASSWORD}

./babylonnode monitoring install -a

sleep 10

grafana_status_code=$(curl -s -o /dev/null -w "%{http_code}\n" localhost:3000/login)
if [[ $grafana_status_code != 200 ]]; then
  echo "Grafana did not start properly. Exiting..."
  exit $grafana_status_code
fi

prometheus_status_code=$(curl -s -o /dev/null -w "%{http_code}\n" localhost:9090/prometheus/graph)
if [[ $prometheus_status_code != "200" ]]; then
  echo "Prometheus did not start properly. Exiting..."
  exit $prometheus_status_code
fi

./babylonnode docker install -u -f $HOME/babylon-node-config/config.yaml -a

echo "Checking container health"
sleep 10
docker ps

echo "Waiting and checking again"
sleep 10
docker ps

#echo "Testing Core node health endpoint"
#set +e
#for i in {1..5}; do
#  FULL_OUTPUT=$(NGINX_ADMIN_PASSWORD=${NGINX_ADMIN_PASSWORD} ./babylonnode api system health)
#  OUTPUT=$(echo $FULL_OUTPUT | jq -r '.status')
#  if [[ $OUTPUT == "SYNCING" || $OUTPUT == "BOOTING_AT_GENESIS" || $OUTPUT == "OUT_OF_SYNC" || $OUTPUT == "BOOTING" || $OUTPUT == "UP" ]]; then
#    echo "The result is successful"
#    echo "The Node is in status $OUTPUT"
#    break
#  else
#    if [[ $i == 5 ]]; then
#      echo "failed to get ready in time."
#      echo "here are the logs of the core node"
#      docker logs $(whoami)-core-1 --tail 100
#      echo "Exiting..."
#      exit 137
#    fi
#    echo "The result is unsuccessful. Waiting and trying again ($i of 5)"
#    echo "Command ./babylonnode api system health resulted in"
#    echo "$FULL_OUTPUT"
#  fi
#  sleep 30
#done
#set -e

docker logs $(whoami)-core-1 --tail 100

echo "Testing postgres is set up correctly"
sudo systemctl status postgresql@12-main.service --no-pager
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U postgres -d radixdlt_ledger -P pager=off -c "\dt"

echo "Testing gateway endpoints available"

echo "Gateway endpoint"
curl -k -u "gateway:${NGINX_GATEWAY_PASSWORD}" https://localhost/gateway | jq

echo "Status endpoint"
curl -X POST -k -u "gateway:${NGINX_GATEWAY_PASSWORD}" https://localhost/status/gateway-status | jq
curl -X POST -k -u "gateway:${NGINX_GATEWAY_PASSWORD}" https://localhost/status/network-configuration | jq

echo "Metrics endpoint"
curl -k -f -u "metrics:${NGINX_METRICS_PASSWORD}" https://localhost/gateway/metrics

# Endpoint does not exist
#curl -k --user "gateway:${NGINX_GATEWAY_PASSWORD}" https://localhost/token/native --header 'Content-Type: application/json' -d '{ "network_identifier":{"network":"${NETWORK_NAME}"}}'

# These dont work if the ledger is lagging behind.
#echo "Stream endpoint"
#curl -k --user "gateway:${NGINX_GATEWAY_PASSWORD}" https://localhost/stream/transactions --header 'Content-Type: application/json' -d '{ "limit_per_page": 5 }'
#echo "Transaction endpoint"
#curl -k --user "gateway:${NGINX_GATEWAY_PASSWORD}" https://localhost/transaction/construction --header 'Content-Type: application/json' -d '{"ledger_state": {"network": "${NETWORK_NAME}","state_version": 0,"proposer_round_timestamp": "string","epoch": 0,"round": 0}}'

./babylonnode optimise-node -s -u -ss 1G

echo "Everything seem to work just fine."
echo "Cleaning up"

df -H
docker system df
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U postgres -d radixdlt_ledger -P pager=off -c "\l+"
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U postgres -d radixdlt_ledger -P pager=off -c "select pg_size_pretty(pg_database_size('radixdlt_ledger'));"

./babylonnode docker stop
./babylonnode monitoring stop

# Wipe database
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U postgres -d postgres -P pager=off -c "DROP DATABASE IF EXISTS radixdlt_ledger;"

# Wipe ledger
sudo rm -rf /home/radixdlt/babylon-ledger/ | true

# Wipe docker image store
docker rmi $(docker image ls -q) | true
