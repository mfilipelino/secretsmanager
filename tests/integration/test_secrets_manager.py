import json
import time

import pytest

from secretsmanager.secretsmanager import build_secrets_service


@pytest.fixture()
def context():
    key = "sandbox/dataplatform/project/pytest-" + str(time.time())
    value = '{"env": "test"}'

    boto3_client = build_secrets_service()._client
    boto3_client.create_secret(
        Name=key,
        SecretString=value
    )
    yield key, value
    boto3_client.delete_secret(
        SecretId=key,
        ForceDeleteWithoutRecovery=True
    )


@pytest.mark.integration
def test_secrets_manager_get_invalidate_key():
    secrets_manager = build_secrets_service()
    with pytest.raises(Exception) as exception_info:
        secrets_manager.get_secret_string("invalid")
    assert exception_info.typename == "ResourceNotFoundException"


@pytest.mark.integration
def test_secrets_manager_get_validate_key(context):
    secrets_manager = build_secrets_service()
    key, value = context
    str_value = secrets_manager.get_secret_string(key)
    assert str_value == value
    value = json.loads(str_value)
    assert value.get("env") == "test"
