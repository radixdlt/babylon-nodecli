#!/bin/bash

# Ledger default folder
DATA_DIR="/data"

# Ensure that the /data directory exists
if [ ! -d "$DATA_DIR" ]; then
    echo "Creating /data directory..."
    mkdir -p "$DATA_DIR"
fi

# Check if /data directory is empty
if [ -z "$(ls -A "$DATA_DIR")" ]; then
    cd $DATA_DIR
    echo "Directory $DATA_DIR is empty. Downloading LedgerSnapshot..."
    # Fetch and execute the latest snapshot script from Radix
    echo "Fetching and executing the latest snapshot script from Radix..."
    curl -s https://snapshots.radix.live/latest-snapshot-NO-INDEX.sh | bash

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


