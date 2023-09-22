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
#export SEED_NODE=radix://node_tdx_e_1q0gm3fwqh8ggl09g7l8ru96krzlxdyrc694mqw8cf227v62vjyrmccv8md5@13.126.65.118,radix://node_tdx_e_1q0juzf2gnhfhy2aj6x88x4f459tf2a2mdk56jm3ffhzp94fn8k0q5lkse34@52.64.209.45,radix://node_tdx_e_1qdzlwtjn9wcmcyt3mp3g4qaerr6fgrl86ze6t20427tf4rmnu670y0cgszc@54.72.0.65,radix://node_tdx_e_1qfz9r8xp95vuzjq503l856ywukrdnukcz4232tr4nsx7ff2efvfnwvaq080@35.168.132.18
#export NETWORK_ID=14
#export NETWORK_NAME=zabanet

export DISABLE_VERSION_CHECK=true
export COMPOSE_HTTP_TIMEOUT=360
#Below PATH require when ansible is installed as part of pip
export PATH="$PATH:/home/ubuntu/.local/bin"

export PROMPT_FEEDS="node-runner-cli/test-prompts/gateway-local-core-remote-postgress.yml"
./babylonnode docker config \
  -m DETAILED \
  -d $HOME/babylon-node-config \
  -k $KEYSTORE_PASSWORD -nk -a

cat $HOME/babylon-node-config/config.yaml

# Reset everything
./babylonnode docker stop -f $HOME/babylon-node-config/config.yaml | true

# Setup passwords details
DOCKER_COMPOSE_FOLDER_PREFIX=$(whoami) ./babylonnode auth set-admin-password -m DOCKER -p ${NGINX_ADMIN_PASSWORD}
DOCKER_COMPOSE_FOLDER_PREFIX=$(whoami) ./babylonnode auth set-metrics-password -m DOCKER -p ${NGINX_METRICS_PASSWORD}
DOCKER_COMPOSE_FOLDER_PREFIX=$(whoami) ./babylonnode auth set-gateway-password -m DOCKER -p ${NGINX_GATEWAY_PASSWORD}

./babylonnode docker install -f $HOME/babylon-node-config/config.yaml -a

echo "Checking container health"
sleep 10
docker ps

echo "Waiting and checking again"
sleep 10
docker ps

echo "Testing Core node health endpoint"
set +e
for i in {1..5}; do
  FULL_OUTPUT=$(NGINX_ADMIN_PASSWORD=${NGINX_ADMIN_PASSWORD} ./babylonnode api system health)
  OUTPUT=$(echo $FULL_OUTPUT | jq -r '.status')
  if [[ $OUTPUT == "SYNCING" || $OUTPUT == "BOOTING_AT_GENESIS" || $OUTPUT == "BOOTING" || $OUTPUT == "UP" ]]; then
    echo "The result is successful"
    echo "The Node is in status $OUTPUT"
    break
  else
    if [[ $i == 5 ]]; then
      echo "failed to get ready in time."
      echo "here are the logs of the core node"
      docker logs $(whoami)-core-1 --tail 100
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

echo "Testing postgres is set up correctly"
PGPASSWORD=$POSTGRES_PASSWORD psql -h postsgres -U postgres -d radixdlt_ledger -P pager=off -c "\dt"

echo "Testing gateway endpoints available"

echo "Gateway endpoint"
curl -k -u "gateway:${NGINX_GATEWAY_PASSWORD}" https://localhost/gateway | jq

echo "Status endpoint"
curl -X POST -k -u "gateway:${NGINX_GATEWAY_PASSWORD}" https://localhost/status/gateway-status | jq
curl -X POST -k -u "gateway:${NGINX_GATEWAY_PASSWORD}" https://localhost/status/network-configuration | jq

echo "Metrics endpoint"
curl -k -f -u "metrics:${NGINX_METRICS_PASSWORD}" https://localhost/gateway/metrics

echo "Everything seem to work just fine."
echo "Cleaning up"

df -H
docker system df
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U postgres -d radixdlt_ledger -P pager=off -c "\l+"
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U postgres -d radixdlt_ledger -P pager=off -c "select pg_size_pretty(pg_database_size('radixdlt_ledger'));"
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U postgres -d radixdlt_ledger -P pager=off -c "select pg_size_pretty(pg_database_size('radixdlt_ledger'));"

./babylonnode docker stop

# Wipe database
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U postgres -d postgres -P pager=off -c "DROP DATABASE IF EXISTS radixdlt_ledger;"

# Wipe ledger
rm -rf /home/radixdlt/babylon-ledger/ | true

# Wipe docker image store
docker rmi $(docker image ls -q) | true