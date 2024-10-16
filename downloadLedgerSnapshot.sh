#!/bin/bash

# Set default data directory if not provided as an argument
DATA_DIR=${1:-"/data"}

# Ensure that the /data directory exists
if [ ! -d "$DATA_DIR" ]; then
    echo "Creating $DATA_DIR directory..."
    mkdir -p "$DATA_DIR"
fi

# Check if /DATA_DIR directory is empty
if [ -z "$(ls -A "$DATA_DIR")" ]; then
    cd $DATA_DIR
    echo "Directory $DATA_DIR is empty. Downloading LedgerSnapshot..."
    # Fetch and execute the latest snapshot script from Radix
    echo "Fetching and executing the latest snapshot script from Radix..."
    wget https://snapshots.radix.live/latest-snapshot-INDEX.sh --no-check-certificate
    echo "Starting snapshot download"
    bash latest-snapshot-INDEX.sh
   
    # Check if the script ran successfully
    if [ $? -eq 0 ]; then
        echo "Snapshot download and execution completed successfully."
    else
        echo "Snapshot download or execution failed."
        exit 1
    fi
else
    echo "Directory $DATA_DIR is not empty. Downloading Ledger Snapshot aborted:"
    ls -l "$DATA_DIR"
fi

tar --use-compress-program=zstdmt -xvf RADIXDB-INDEX.tar.zst --exclude=./address_book -C .
rm -rf RADIXDB-INDEX.*
rm -rf latest-snapshot-INDEX.sh*
echo "Snapshot restored"


