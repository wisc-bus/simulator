from .baseManager import BaseManager
import os
import json
import time
from zipfile import ZipFile
import pandas as pd
from subprocess import check_output
import boto3


class AWSManager(BaseManager):
    def __init__(self, gtfs_path, city_path, out_path):
        self._s3 = boto3.client('s3')
        self._iam = boto3.client("iam")
        self._lambda = boto3.client('lambda', region_name='ap-northeast-1')
        self.bucket_name = self._create_bucket()
        # self._upload_data(gtfs_path, city_path)
        self._upload_lambda()

    def read_gtfs(self, filename):
        pass

    def read_city(self):
        pass

    def save(self, result):
        pass

    def clean_up(self):
        print("cleaning up aws resources")
        self._clean_bucket()
        self._clean_lambda()

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
        # self._upload_lambda_layer()
        self._upload_lambda_function()

    def _upload_lambda_layer(self):
        print("packaging lambda layer")
        self.layerName = "busSim-layer"

        lambda_path = self._get_lambda_path()
        check_output(["./deploy_layer.sh"], cwd=lambda_path)
        zip_path = os.path.join(
            lambda_path, "lambda_layers", "busSim-layer.zip")

        print("deploying lambda layer")
        with open(zip_path, 'rb') as f:
            self._lambda.publish_layer_version(
                LayerName=self.layerName,
                Description='The layer needed for busSim',
                Content={
                    'ZipFile': f.read()
                },
                CompatibleRuntimes=[
                    'python3.8',
                ]
            )

    def _upload_lambda_function(self):
        self.roleName = 's3rwRole'
        self.policyName = 's3rwPolicy'
        self.functionName = 'busSim'

        # create IAM role
        print("creating IAM role")
        response = self._iam.create_role(
            RoleName=self.roleName,
            AssumeRolePolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
        )
        self.roleArn = response.get("Role").get("Arn")

        # create policy
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "ListObjectsInBucket",
                    "Effect": "Allow",
                    "Action": ["s3:ListBucket"],
                    "Resource": [f"arn:aws:s3:::{self.bucket_name}"]
                },
                {
                    "Sid": "AllObjectActions",
                    "Effect": "Allow",
                    "Action": "s3:*Object",
                    "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                }
            ]
        }
        response = self._iam.create_policy(
            PolicyName=self.policyName,
            PolicyDocument=json.dumps(policy)
        )
        self.policyArn = response.get("Policy").get("Arn")

        # attach policy
        self._iam.attach_role_policy(
            PolicyArn=self.policyArn,
            RoleName=self.roleName
        )

        # package function
        print("packaging lambda function")
        lambda_path = self._get_lambda_path()

        tmp = 'tmp.zip'
        with ZipFile(tmp, 'w') as z:
            for name in (n for n in os.listdir(lambda_path) if n.split('.')[-1] == 'py'):
                z.write(os.path.join(lambda_path, name), '/'+name)

        print("deploying lambda function")
        time.sleep(10)
        with open(tmp, 'rb') as f:
            response = self._lambda.create_function(
                Code={
                    'ZipFile': f.read()
                },
                Description='BusSim handler',
                FunctionName=self.functionName,
                Handler='lambda_function.lambda_handler',
                MemorySize=512,
                Publish=True,
                Role=self.roleArn,
                Runtime='python3.8',
                Timeout=900,
                TracingConfig={
                    'Mode': 'Active',
                },
            )

        os.remove(tmp)

    def _clean_bucket(self):
        print("cleaning up s3")
        self._s3.delete_bucket(
            Bucket=self.bucket_name
        )

    def _clean_lambda(self):
        print("cleaning up lambda")
        self._iam.detach_role_policy(
            RoleName=self.roleName,
            PolicyArn=self.policyArn
        )

        self._iam.delete_policy(
            PolicyArn=self.policyArn
        )

        self._iam.delete_role(
            RoleName=self.roleName
        )

        self._lambda.delete_function(
            FunctionName=self.functionName
        )

    def _get_lambda_path(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        lambda_path = os.path.join(
            dir_path, os.pardir, os.pardir, os.pardir, "lambda")
        return lambda_path

    def _get_account_id(self):
        sts = boto3.client('sts')
        return sts.get_caller_identity()['Account']
