from .baseManager import BaseManager
import os
import json
import time
from zipfile import ZipFile
import pandas as pd
from subprocess import check_output
import boto3
import docker
import base64


class AWSManager(BaseManager):
    ROLE_NAME = 's3rwRole'
    POLICY_NAME = 's3rwPolicy'
    FUNCTION_NAME = 'busSim'
    REPO_BASENAME = "scanalyzer-lambda-handler"
    PUBLIC_REPOSITORY = 'public.ecr.aws/o8i2z7h9/scanalyzer-lambda-handler'
    ECR_USERNAME = 'AWS'

    def __init__(self, gtfs_path, out_path, borders):
        self._s3 = boto3.client('s3')
        self._iam = boto3.client("iam")
        self._ecr = boto3.client('ecr', region_name='ap-northeast-1')
        self._lambda = boto3.client('lambda', region_name='ap-northeast-1')
        # self.bucket_name = self._create_bucket()
        # # self._upload_data(gtfs_path, city_path)
        # self._upload_lambda()

    def run_batch(self, config, perf_df=None):
        pass
        # if perf_df:
        #     print("perf in AWS env not supported")
        # start_times = config.get_start_times()

        # result_df = pd.DataFrame(
        #     columns=["geometry", "start_time", "map_identifier"])

        # for start_time in start_times:
        #     # async call lambda handler
        #     for stop_idx, start_point in enumerate(start_points):
        #         # immediatly add "geometry", "start_time", "map_identifier" to result df

        # return result_df

    def read_gtfs(self):
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
        bucket_name = f"bussim-{account_id}"

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
        self.roleArn, self.policyArn = self._create_lambda_role()
        self.repo_uri = self._create_repo()
        self._upload_image()
        self._upload_lambda_function()

    def _create_lambda_role(self):
        # create IAM role
        print("creating IAM role")
        response = self._iam.create_role(
            RoleName=self.ROLE_NAME,
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
        roleArn = response.get("Role").get("Arn")

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
            PolicyName=self.POLICY_NAME,
            PolicyDocument=json.dumps(policy)
        )
        policyArn = response.get("Policy").get("Arn")

        # attach policy
        self._iam.attach_role_policy(
            PolicyArn=policyArn,
            RoleName=self.ROLE_NAME
        )

        return roleArn, policyArn

    def _create_repo(self):
        response = self._ecr.create_repository(
            repositoryName=self.REPO_BASENAME
        )

        return response["repository"]["repositoryUri"]

    def _upload_image(self):
        '''
        1.Pull Docker image from the offical public ECR repo 
        2.Push to a private ECR repo (pulic image URI not supported for creating a lambda function)
        '''
        print("uploading the image")

        # get ecr credentials
        ecr_credentials = self._ecr.get_authorization_token()[
            'authorizationData'][0]
        ecr_password = (
            base64.b64decode(ecr_credentials['authorizationToken'])
            .replace(b'AWS:', b'')
            .decode('utf-8'))
        ecr_url = ecr_credentials['proxyEndpoint']

        # pull the image from the offical public ECR repo
        docker_client = docker.from_env()
        docker_client.login(
            username=self.ECR_USERNAME, password=ecr_password, registry=ecr_url)
        image = docker_client.images.pull(repository=self.PUBLIC_REPOSITORY)

        # push to a private ECR repo
        image.tag(self.repo_uri, tag='latest')
        push_log = docker_client.images.push(self.repo_uri, tag='latest')

    def _upload_lambda_function(self):
        print("deploying lambda function")
        response = self._lambda.create_function(
            Code={
                'ImageUri': "public.ecr.aws/o8i2z7h9/scanalyzer-lambda-handler:latest"
            },
            PackageType="Image",
            FunctionName=self.FUNCTION_NAME,
            MemorySize=512,
            Role=self.roleArn,
            Timeout=900,
            TracingConfig={
                'Mode': 'Active',
            },
        )

    def _clean_bucket(self):
        print("cleaning up s3")
        self._s3.delete_bucket(
            Bucket=self.bucket_name
        )

    def _clean_lambda(self):
        print("cleaning up lambda")
        self._iam.detach_role_policy(
            RoleName=self.ROLE_NAME,
            PolicyArn=self.policyArn
        )

        self._iam.delete_policy(
            PolicyArn=self.policyArn
        )

        self._iam.delete_role(
            RoleName=self.ROLE_NAME
        )

        self._lambda.delete_function(
            FunctionName=self.FUNCTION_NAME
        )

        self._ecr.delete_repository(
            repositoryName=self.REPO_BASENAME,
            force=True
        )

    def _get_lambda_path(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        lambda_path = os.path.join(
            dir_path, os.pardir, os.pardir, os.pardir, "lambda")
        return lambda_path

    def _get_account_id(self):
        sts = boto3.client('sts')
        return sts.get_caller_identity()['Account']
