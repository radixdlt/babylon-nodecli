import os
import subprocess
import tarfile

def download_and_extract_snapshot(data_dir):
    if not os.path.isdir(data_dir):
        print(f"Creating {data_dir} directory...")
        os.makedirs(data_dir)

    if not os.listdir(data_dir):
        os.chdir(data_dir)
        print(f"Directory {data_dir} is empty. Downloading LedgerSnapshot...")
        print("Fetching and executing the latest snapshot script from Radix...")
        subprocess.run(["wget", "https://snapshots.radix.live/latest-snapshot-INDEX.sh", "--no-check-certificate"], check=True)
        print("Starting snapshot download")
        result = subprocess.run(["bash", "latest-snapshot-INDEX.sh"])

        if result.returncode == 0:
            print("Snapshot download and execution completed successfully.")
        else:
            print("Snapshot download or execution failed.")
            exit(1)

        with tarfile.open("RADIXDB-INDEX.tar.zst", "r:zstd") as tar:
            tar.extractall(path=".", members=[m for m in tar.getmembers() if not m.name.startswith('./address_book')])
        
        os.remove("RADIXDB-INDEX.tar.zst")
        os.remove("latest-snapshot-INDEX.sh")
        print("Snapshot restored")
    else:
        print(f"Directory {data_dir} is not empty. Downloading Ledger Snapshot aborted:")
        for item in os.listdir(data_dir):
            print(item)

