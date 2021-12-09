import logging
import os

import boto3
from botocore.exceptions import ClientError

logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class SecretsService(object):
    """ Wrapper for AWS Secrets Manager """

    SERVICE_NAME = "secretsmanager"

    def __init__(self, client, region_name: str) -> None:
        """
        :param region_name:
        """
        self._client = client(
            service_name=self.SERVICE_NAME,
            region_name=region_name
        )

    def _get_secret_value_response(self, secret_id: str):
        try:
            get_secret_value_response = self._client.get_secret_value(
                SecretId=secret_id
            )
        except ClientError as e:
            logging.error(e.response.get("Error").get("Message"))
            raise e
        else:
            return get_secret_value_response

    def get_secret_string(self, secret_id: str) -> str:
        """
        :param secret_id:
        :return:
        """
        secret_value_response = self._get_secret_value_response(secret_id)
        return secret_value_response['SecretString'] if 'SecretString' in secret_value_response else None


def _create_boto3_client():
    env = os.environ.get("ENV", "sandbox")
    if env == "sandbox":
        boto3.setup_default_session(profile_name=env)
        return boto3.client
    else:
        boto3.session.Session(
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
        )
        return boto3.client()


def build_secrets_service():
    return SecretsService(client=_create_boto3_client(), region_name=os.environ.get("REGION", "us-west-2"))
