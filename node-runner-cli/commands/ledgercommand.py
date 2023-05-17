from argparse import ArgumentParser
from argparse import RawTextHelpFormatter

import botocore

from commands.subcommand import get_decorator, argument

import boto3
from botocore import UNSIGNED
from botocore.client import Config


BUCKET_NAME = 'backup-mainnet-ledger'
BUCKET_FULLNODE_FOLDER = 'mainnet/mainnet_eu_west_1_fullnode3'
BUCKET_VALIDATOR_FOLDER = 'mainnet/mainnet_eu_west_1_fullnode2'



ledgercli = ArgumentParser(
    description='Subcommand to help to sync up the ledger of a fullnode or validator from a copy',
    usage="radixnode ledger ",
    formatter_class=RawTextHelpFormatter)
ledger_parser = ledgercli.add_subparsers(dest="ledgercommand")


def ledgercommand(ledgercommand_args=[], parent=ledger_parser):
    return get_decorator(ledgercommand_args, parent)


@ledgercommand([
    argument("-t", "--type",
             help="Type of node of the backup ledger you want to download.For fullnode it is fullnode and for validator it is validator."
                  "If not provided you will be prompted to enter a value ",
             action="store", 
             default=""),
    argument("-d", "--dest",
             help="Destination path where the backup of the ledger will be downloaded ",
             action="store", 
             default="")
])
def sync(args):
    """
    This commands allows node-runners and gateway admins to create a config file, which can persist their custom settings.
    Thus it allows is to decouple the updates from configuration.
    Config is created only once as such and if there is a version change in the config file,
    then it updated by doing a migration to newer version
    """
    print("SYNC function")
    type = args.type
    dest = args.dest
    if len(type) == 0:
        print("NO ARGUMENTS")
        ##configuration.common_config.ask_network_id(args.type)
    if type == "fullnode":
        print("Downloading fullnode ledger...")
        download_mainnet_backup_ledger(True, dest)

    elif type == "validator":
        print("Downloading validator ledger...")
        download_mainnet_backup_ledger(False, dest)



def download_mainnet_backup_ledger(fullnode: bool, destinationPath: str):

#     """
#     Downloads validator or fullnode mainnet ledger into destinationPath
#     :param fullnode: Indicates if the ledger to be downloaded should be from a fullnode
#     :param destinationPath: Local path to be downloaded the ledger
#     """

    BUCKET_FOLDER = BUCKET_FULLNODE_FOLDER if fullnode else BUCKET_VALIDATOR_FOLDER

    try:
        s3_client = boto3.client("s3", config=Config(signature_version=UNSIGNED))
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME,Prefix=BUCKET_FOLDER)
    except Exception as err:
        logging.error('Exception was thrown in connection %s' % err)
        print("Error is {}".format(err))
        return err
    
    files = response.get("Contents")
    if not files:
         raise Exception("Error downloading a copy of the ledger, Bucket/Folder not found or empty")
    else:
        for file in files:
            print(f"file_name: {file['Key']}, size: {file['Size']}")
            if file['Size'] > 0:
                try: 
                    url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file['Key']}"
                    filename = file['Key'].split('/')[-1]  # get filename from key
                    print(f"Downloading file: {file['Key']}, size: {file['Size']}")            
                    s3_client.download_file(BUCKET_NAME, BUCKET_FOLDER+"/"+filename, destinationPath + filename)
                except botocore.exceptions.ClientError as error:
                    print(error.response['Error']['Code']) #a summary of what went wrong
                    print(error.response['Error']['Message']) #explanation of what went wrong
                    return False