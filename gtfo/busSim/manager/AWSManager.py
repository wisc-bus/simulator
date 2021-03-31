from .baseManager import BaseManager
import os
import pandas as pd
import boto3


class AWSManager(BaseManager):
    def __init__(self, gtfs_path, city_path, out_path):
        self._s3 = boto3.client('s3')
        self.bucket_name = self._create_bucket()
        self._upload_data(gtfs_path, city_path)
        self._upload_lambda()

    def read_gtfs(self, filename):
        pass

    def read_city(self):
        pass

    def save(self, result):
        pass

    def _create_bucket(self):
        print("creating s3 bucket")
        account_id = self._get_account_id()
        bucket_name = f"gtfs-bussim-{account_id}"

        self._s3.create_bucket(
            Bucket=bucket_name,
        )

        return bucket_name

    def _upload_data(self, gtfs_path, city_path):
        print("uploading data")
        with open(gtfs_path, 'rb') as f:
            self._s3.put_object(Bucket=self.bucket_name,
                                Key="gtfs.zip",
                                Body=f)

    def _upload_lambda(self):
        pass

    def _get_account_id(self):
        sts = boto3.client('sts')
        return sts.get_caller_identity()['Account']
