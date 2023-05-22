from argparse import ArgumentParser
from argparse import RawTextHelpFormatter

import botocore

from commands.subcommand import get_decorator, argument

import boto3

ledgercli = ArgumentParser(
    description='Subcommand to help to sync up the ledger of a fullnode or validator from a copy',
    usage="radixnode ledger ",
    formatter_class=RawTextHelpFormatter)
ledger_parser = ledgercli.add_subparsers(dest="ledgercommand")


def ledgercommand(ledgercommand_args=[], parent=ledger_parser):
    return get_decorator(ledgercommand_args, parent)


@ledgercommand([
    argument("-d", "--dest",
             help="Destination path where the backup of the ledger will be downloaded ",
             action="store", 
             default="./"),
    argument("-bn", "--bucketname",
             help="S3 bucket name to download the backup of the ledger from",
             action="store",
             default=""),
    argument("-bf", "--bucketfolder",
             help="S3 bucket folder to download the backup of the ledger from",
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
    bucketName = args.bucketname
    bucketFolder = args.bucketfolder
    dest = args.dest
    if len(bucketName) == 0:
        print("No S3 bucket was indicated")
    else:
        print(f"Downloading backup ledger {bucketName}  {bucketFolder} ...")
        download_mainnet_backup_ledger(bucketName, bucketFolder, dest)



def download_mainnet_backup_ledger(bucketName: str, bucketFolder: str, destinationPath: str):

#     """
#     Downloads validator or fullnode mainnet ledger into destinationPath
#     :param bucketName: Indicates the name of the s3 bucket that contains the backup ledger to download
#     :param bucketFolder: Indicates the folder inside the s3 bucket that contains the backup ledger to download
#     :param destinationPath: Local path to be downloaded the ledger
#     """
    try:
        s3_client = boto3.client("s3")
        response = s3_client.list_objects_v2(Bucket=bucketName,Prefix=bucketFolder)
        print(response)
    except Exception as err:
       ## logging.error('Exception was thrown in connection %s' % err)
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
                    filename = file['Key'].split('/')[-1]  # get filename from key
                    print(f"Downloading file: {file['Key']}, size: {file['Size']}")
                    s3_client.download_file(bucketName, bucketFolder+"/"+filename, destinationPath + filename)
                except botocore.exceptions.ClientError as error:
                    print(error.response['Error']['Code']) #a summary of what went wrong
                    print(error.response['Error']['Message']) #explanation of what went wrong
                    return False