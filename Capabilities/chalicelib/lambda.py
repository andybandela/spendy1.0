import boto3  # AWS SDK for Python
from boto3.dynamodb.conditions import Key  # For working with DynamoDB keys

dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
dynamodb_table = boto3.resource('dynamodb', region_name='us-east-1').Table('spendy_users')

def lambda_handler(event, context):
    table_name = 'spendy_user'

    user_id = event['request']['userAttributes']['sub']
    email = event['request']['userAttributes']['email']

    item = {
        'user_id': user_id,  # Assuming 'userId' is the primary key
        'email': email
    }

    try:
        dynamodb_table.put_item(Item=item)
        print(f"User {user_id} added to table {table_name}")
    except Exception as e:  # More general exception handling
        print(f"Error adding user {user_id} to table {table_name}: {e}")
        raise Exception(f"Error adding user to table: {e}")

    return event 
