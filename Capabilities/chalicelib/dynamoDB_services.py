import boto3
from botocore.exceptions import ClientError
import logging
import json
from decimal import Decimal
from collections import defaultdict
from boto3.dynamodb.conditions import Key, Attr



logger = logging.getLogger(__name__)

class Receipts:
    def __init__(self):
        self.dyn_resource = boto3.resource('dynamodb',region_name='us-east-1')
        # The table variable is set during the scenario in the call to
        # 'exists' if the table exists. Otherwise, it is set by 'create_table'.
        #self.table_user = self.dyn_resource.Table('spendy_user_info')
        self.table_receipts = self.dyn_resource.Table('spendy_receipt_info')
        self.table_expenses = self.dyn_resource.Table('spendy_expenses')
        #self.table_user.load()
        self.table_receipts.load()
        self.table_expenses.load()
    
    def add_receipt(self,items):
        try:
            self.table_receipts.put_item(
                Item=items
            )
            body = {
                'Operation': 'SAVE',
                'Message': 'SUCCESS',
                'Item': items
            }

            return self.build_response(200,body)

        except ClientError as err:
            logger.error(
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    def add_expense(self,items):
        try:
            self.table_expenses.put_item(
                Item=items
            )
            body = {
                'Operation': 'SAVE',
                'Message': 'SUCCESS',
                'Item': items
            }

            return self.build_response(200,body)

        except ClientError as err:
            logger.error(
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
    
    
    def get_most_bought_item(self,user_id):
        try:
            item_totals = defaultdict(float)
            response = self.table_expenses.scan(FilterExpression=boto3.dynamodb.conditions.Attr('user_id').eq(user_id))
            
            for item in response['Items']:
                item_name = item['item']
                item_price = float(item['price'])
                item_totals[item_name] += item_price
            most_bought_item = max(item_totals, key=item_totals.get)
            total_spent = item_totals[most_bought_item]
            return most_bought_item, total_spent
        except ClientError as err:
            logger.error(err.response["Error"]["Code"], err.response["Error"]["Message"])
            raise
    
    def get_all_rows(self):
        try:
            response = self.table_expenses.scan()
            items = response['Items']
            return items
        except ClientError as err:
            logger.error(err.response["Error"]["Code"], err.response["Error"]["Message"])
            raise
    def get_all_rows1(self, user_id):
        try:
            if user_id:
                response = self.table_expenses.scan(FilterExpression=boto3.dynamodb.conditions.Attr('user_id').eq(user_id))
                #res = self.table_expenses.query(KeyConditionExpression=Attr('user_id').eq(user_id))
                #print(res)
                print(response)
            else:
                response = {'Items':{}}
            items = response['Items']
            return items
        except ClientError as err:
            logger.error(err.response["Error"]["Code"], err.response["Error"]["Message"])
            raise




    @staticmethod
    def build_response(status_code, body):
        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(body, cls=DecimalEncoder)
        }
    
    


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Check if it's an int or a float
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        # Let the base class default method raise the TypeError
        return super(DecimalEncoder, self).default(obj)

