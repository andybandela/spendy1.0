import boto3
import logging
from botocore.exceptions import ClientError
import json
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class TextractService:
    def __init__(self,storage_service):
        self.client = boto3.client('textract')
        self.bucket_name = storage_service.get_storage_location()
    
    def analyse_receipt(self,filename):
        response = self.client.analyze_expense(Document={'S3Object': {'Bucket': self.bucket_name, 'Name': filename}})
        re = Response(response)
        re.update_fields()
        return re.return_values()
    

class Response:
    def __init__(self,response_data):
        self.response = response_data
        self.items = []
        self.prices = []
        self.summary = {}
    
    @staticmethod
    def get_items(field):
        
        item = None
        price = None
        if "ValueDetection" in field:
            if str(field.get("Type")["Text"]) == "ITEM":
                item = str(field.get("ValueDetection")["Text"])
            elif str(field.get("Type")["Text"]) == "PRICE":
                tempprice = field.get("ValueDetection")["Text"]
                price = re.sub(r'\$', '', str(tempprice))
        return item, price
        
        
    #@staticmethod
    def get_summary(self,field):
        try:
            date = {}
            total = {}
            vendor = {}
            if "ValueDetection" in field:
                if str(field.get("Type")["Text"]) == "INVOICE_RECEIPT_DATE":
                    temp = field.get("ValueDetection")["Text"]
                    temp = str(self.standardize_date(temp))
                    date = {"date":temp}
                    return date
                elif str(field.get("Type")["Text"]) == "TOTAL":
                    temptotal = field.get("ValueDetection")["Text"]
                    tot = re.sub(r'\$', '', str(temptotal))
                    total = {"total":tot}
                    return total
                elif str(field.get("Type")["Text"]) == "VENDOR_NAME":
                    if field.get("ValueDetection")["Confidence"] > 99.55:
                        vendor = {"vendor":field.get("ValueDetection")["Text"]}
                        return vendor
        except ClientError as err:
            logger.error(
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
    
    def update_fields(self):
        try:
            for expense_doc in self.response["ExpenseDocuments"]:
                    for line_item_group in expense_doc["LineItemGroups"]:
                        for line_items in line_item_group["LineItems"]:
                            for expense_fields in line_items["LineItemExpenseFields"]:
                                
                                
                                item,price = self.get_items(expense_fields)
                                if item is not None:
                                    self.items.append(item)
                                if price is not None:
                                    self.prices.append(price)

                    for summary_field in expense_doc["SummaryFields"]:
                        temp = self.get_summary(summary_field)
                        print('Error Start')
                        print(temp)
                        print()
                        if temp is not None:
                            for t in temp:
                                self.summary[t] = temp[t]
        except ClientError as err:
            logger.error(
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
    
    def return_values(self):
        print(self.items,"\n",self.prices,"\n",self.summary)
        items = []
        for i in range(len(self.items)):
            items.append({'item':self.items[i],'price':self.prices[i],'date': self.summary['date'],'vendor': self.summary['vendor']})
        response = {
            'date': self.summary['date'],
            'total':self.summary['total'],
            'vendor': self.summary['vendor'],
            'items': items
        }
        return response
    @staticmethod
    def standardize_date(date_str):
        try:
            
            date_obj = datetime.strptime(date_str, '%d/%m/%y')
            return date_obj.strftime('%Y-%m-%d')  
        except ValueError:
            try:
                
                date_obj = datetime.strptime(date_str, '%m/%d/%y')
                return date_obj.strftime('%Y-%m-%d')  
            except ValueError:
                return None  

