import boto3

s3 = boto3.client('s3')


def lambda_handler(event, context):
    response = s3.get_object(
        Bucket='gtfs-bussim-347664766527',
        Key='config.sh',
    )

    print(str(response.get("Body").read()))
