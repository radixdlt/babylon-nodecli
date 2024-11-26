import os
import subprocess
import tarfile
import zstandard as zstd
import requests
import time


def download_and_extract_snapshot(data_dir):
    if not os.path.isdir(data_dir):
        print(f"Creating {data_dir} directory...")
        os.makedirs(data_dir)

    if not os.listdir(data_dir):
        os.chdir(data_dir)
        print(f"Directory {data_dir} is empty. Downloading LedgerSnapshot...")
        radix_live_download()
    else:
        print(f"Directory {data_dir} is not empty. Downloading Ledger Snapshot aborted:")
        for item in os.listdir(data_dir):
            print(item)

def radix_live_download():
    print("Fetching and executing the latest snapshot script from Radix...")
    if not os.path.isfile("RADIXDB-INDEX.tar.zst"):
            #refactor to use requests
        url = "https://snapshots.radix.live/latest-snapshot-INDEX.sh"
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            with open("latest-snapshot-INDEX.sh", "wb") as file:
                file.write(response.content)
        else:
            print(f"Failed to download the snapshot script. Status code: {response.status_code}")
            exit(1)
        print("Starting snapshot download")
            
            
        result = subprocess.run(["bash", "latest-snapshot-INDEX.sh"])
        if result.returncode == 0:
            print("Snapshot download and execution completed successfully.")
        else:
            print("Snapshot download or execution failed.")
            exit(1)
    else:
        print("RADIXDB-INDEX.tar.zst already exists, skipping download.")
        
    print("Extracting snapshot...")
    dctx = zstd.ZstdDecompressor() 
    download_start_time = time.time()
    with open("RADIXDB-INDEX.tar.zst", "rb") as compressed_file:
        start_time = time.time()
        total_extracted_size = 0

        with dctx.stream_reader(compressed_file) as reader:
            with tarfile.open(fileobj=reader, mode='r|') as tar:
                extracted_members = 0
                for member in tar:
                    if member.name.startswith('./address_book'):
                        continue
                    member_path = os.path.join(".", member.name)
                    if not os.path.exists(member_path):
                        tar.extract(member, path=".")
                        extracted_members += 1
                        extracted_size = os.path.getsize(member_path)
                        total_extracted_size += extracted_size
                        # print(f"Extracted {member.name} with size {extracted_size} bytes.")
                    if time.time() - start_time >= 180:  # 3 minutes
                        print(f"{total_extracted_size / (1024 * 1024):.2f} MB extracted so far.")
                        start_time = time.time()
    
    os.remove("RADIXDB-INDEX.tar.zst")
    os.remove("latest-snapshot-INDEX.sh")
    print(f"Snapshot extracted successfully in {time.time() - download_start_time:.2f} seconds.")

