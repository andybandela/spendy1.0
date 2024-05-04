import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class CognitoService:
    def __init__(self):
        self.client = boto3.client('cognito-idp',region_name='us-east-1')
        self.access_token = None
        self.id_token = None

    def getUser(self, access):
        self.access_token = access
        try:
            response = self.client.get_user(AccessToken=self.access_token)
            return response
        except ClientError as err:
            logger.error(
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
