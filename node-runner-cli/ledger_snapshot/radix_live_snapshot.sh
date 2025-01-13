
apt-get update && apt-get install -y \
                wget \
                zstd \
                bash \
                build-essential \
                curl \
                bash \ 
                aria2 \
                zstd \
                && rm -rf /var/lib/apt/lists/*
            # Create the /usr/local/scripts directory
mkdir -p /usr/local/scripts
            RUN echo '#!/bin/bash
            DATA_DIR=$${1:-"/data"}
            if [ ! -d "$$DATA_DIR" ]; then
                echo "Creating $$DATA_DIR directory..."
                mkdir -p "\$$DATA_DIR"
            fi

            if [ -z "$(ls -A "$$DATA_DIR")" ]; then
                cd $$DATA_DIR
                echo "Directory $$DATA_DIR is empty. Downloading LedgerSnapshot..."
                echo "Fetching and executing the latest snapshot script from Radix..."
                wget https://snapshots.radix.live/latest-snapshot-INDEX.sh --no-check-certificate
                echo "Starting snapshot download"
                bash latest-snapshot-INDEX.sh
              
                if [ $? -eq 0 ]; then
                    echo "Snapshot download and execution completed successfully."
                else
                    echo "Snapshot download or execution failed."
                    exit 1
                fi
                tar --use-compress-program=zstdmt -xvf RADIXDB-INDEX.tar.zst --exclude=./address_book -C .
                rm -rf RADIXDB-INDEX.*
                rm -rf latest-snapshot-INDEX.sh*
                echo "Snapshot restored"
            else
                echo "Directory $$DATA_DIR is not empty. Downloading Ledger Snapshot aborted:"
                ls -l "$$DATA_DIR" 
            fi