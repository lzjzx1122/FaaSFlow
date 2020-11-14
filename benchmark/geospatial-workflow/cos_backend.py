import ibm_boto3
from ibm_boto3.s3.transfer import TransferConfig


class COSBackend:
    def __init__(self, endpoint_url, aws_access_key_id, aws_secret_access_key):

        session = ibm_boto3.Session(aws_access_key_id=aws_access_key_id,
                                    aws_secret_access_key=aws_secret_access_key)

        self.cos_client = session.client("s3", endpoint_url=endpoint_url)

        self.cos_resource = session.resource("s3",
                                             aws_access_key_id=aws_access_key_id,
                                             aws_secret_access_key=aws_secret_access_key,
                                             endpoint_url=endpoint_url)

    def list_keys_prefix(self, bucket, prefix):
        res = self.cos_client.list_objects(Bucket=bucket, Prefix=prefix)
        keys = [obj['Key'] for obj in res['Contents']] if 'Contents' in res else []
        return keys

    def upload_file(self, filename, bucket, key):
        tc = TransferConfig()
        self.cos_client.upload_file(filename, bucket, key, Config=tc)

    def download_file(self, bucket, key, filename):
        tc = TransferConfig()
        self.cos_resource.Bucket(bucket).download_file(Key=key, Filename=filename, Config=tc)

    def get_object(self, bucket, key, byte_range=None):
        if byte_range:
            obj = self.cos_client.get_object(Bucket=bucket, Key=key, Range=byte_range)
        else:
            obj = self.cos_client.get_object(Bucket=bucket, Key=key)

        return obj['Body']
