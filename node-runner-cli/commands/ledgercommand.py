from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
from ledger_snapshot import download_and_extract_snapshot
from utils.utils import Helpers
import boto3
import botocore

from commands.subcommand import get_decorator, argument

ledgercli = ArgumentParser(
    description="Subcommand to assist with ledger download",
    usage="babylonnode ledger ",
    formatter_class=RawTextHelpFormatter,
)
ledger_parser = ledgercli.add_subparsers(dest="ledgercommand")


def ledgercommand(ledgercommand_args=[], parent=ledger_parser):
    return get_decorator(ledgercommand_args, parent)


@ledgercommand(
    [
        argument(
            "-d",
            "--dest",
            required=True,
            help="Destination path where the backup of the ledger will be downloaded ",
            action="store",
        ),
        argument(
            "-bn",
            "--bucketname",
            required=True,
            help="S3 bucket name to download the backup of the ledger from",
            action="store",
        ),
        argument(
            "-bf",
            "--bucketfolder",
            help="S3 bucket folder to download the backup of the ledger from",
            action="store",
            default="",
        ),
    ]
)
def s3_download(args):
    """
    Downloads a backuped ledger from an S3 bucket.
    Args:
        args: An object containing the following attributes:
            - bucketname (str): The name of the S3 bucket.
            - bucketfolder (str): The folder within the S3 bucket.
            - dest (str): The destination path where the backup ledger will be downloaded.
    Raises:
        ValueError: If the bucket name is not provided.
    Example:
        args = Namespace(bucketname='my-bucket', bucketfolder='backups', dest='/local/path')
        s3_download(args)
    """

    bucketName = args.bucketname
    bucketFolder = args.bucketfolder
    dest = args.dest
    if len(bucketName) == 0:
        print("No S3 bucket was indicated")
    else:
        print(f"Downloading backup ledger {bucketName}  {bucketFolder} ...")
        s3_fetch_ledger_files(bucketName, bucketFolder, dest)


def s3_fetch_ledger_files(bucketName: str, bucketFolder: str, destinationPath: str):
    #     """
    #     Downloads validator or fullnode mainnet ledger into destinationPath
    #     :param bucketName: Indicates the name of the s3 bucket that contains the backup ledger to download
    #     :param bucketFolder: Indicates the folder inside the s3 bucket that contains the backup ledger to download
    #     :param destinationPath: Local path to be downloaded the ledger
    #     """
    try:
        s3_client = boto3.client("s3")
        response = s3_client.list_objects_v2(Bucket=bucketName, Prefix=bucketFolder)
    except Exception as err:
        print("Error is {}".format(err))
        return err

    files = response.get("Contents")
    if not files:
        raise Exception(
            "Error downloading a copy of the ledger, Bucket/Folder not found or empty"
        )
    else:
        if len(bucketFolder) > 0:
            bucketFolder = bucketFolder + "/"
        for file in files:
            print(f"file_name: {file['Key']}, size: {file['Size']}")
            if file["Size"] > 0:
                try:
                    filename = file["Key"].split("/")[-1]  # get filename from key
                    print(f"Downloading file: {file['Key']}, size: {file['Size']}")
                    s3_client.download_file(
                        bucketName, bucketFolder + filename, destinationPath + filename
                    )
                except botocore.exceptions.ClientError as error:
                    print(
                        error.response["Error"]["Code"]
                    )  # a summary of what went wrong
                    print(
                        error.response["Error"]["Message"]
                    )  # explanation of what went wrong
                    return False


@ledgercommand(
    [
        argument(
            "-d",
            "--dest",
            help="Destination path where the backup of the ledger will be downloaded ",
            action="store",
            default=f"{Helpers.get_default_ledger_dir()}",
        ),
        argument(
            "-s",
            "--source",
            default="radix.live",
            choices=["radix.live"],
            action="store",
            help="Source to download the ledger from. Radix.live is the only supported source at the moment.",
        ),
    ]
)
def fetch_community_snapshot(args):
    """
    Downloads the latest community snapshot of the ledger.
    Args:
        args: An object containing the following attributes:
            - dest (str): The destination path where the backup ledger will be downloaded.
    Raises:
        ValueError: If the source is not provided.
    Example:
        args = Namespace(dest='/local/path')
        download_and_extract_snapshot(args)
    """
    download_and_extract_snapshot(args.dest)
