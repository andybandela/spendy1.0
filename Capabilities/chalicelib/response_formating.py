class Response:
    def __init__(self,response_data):
        self.response = response_data
        self.items = []
        self.prices = []
        self.summary = {}
    
    def get_items(field):
        item = None
        price = None
        if "ValueDetection" in field:
            if str(field.get("Type")["Text"]) == "ITEM":
                item = str(field.get("ValueDetection")["Text"])
            elif str(field.get("Type")["Text"]) == "PRICE":
                price = field.get("ValueDetection")["Text"]
        return item, price
    
    def get_summary(field):
        date = {}
        total = {}
        vendor = {}
        if "ValueDetection" in field:
            if str(field.get("Type")["Text"]) == "INVOICE_RECEIPT_DATE":
                date = {"date":field.get("ValueDetection")["Text"]}
                return date
            elif str(field.get("Type")["Text"]) == "TOTAL":
                total = {"total":field.get("ValueDetection")["Text"]}
                return total
            elif str(field.get("Type")["Text"]) == "VENDOR_NAME":
                if field.get("ValueDetection")["Confidence"] > 99.55:
                    vendor = {"vendor":field.get("ValueDetection")["Text"]}
                    return vendor
    
    def update_fields(self):
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
                    if temp is not None:
                        for t in temp:
                            self.summary[t] = temp[t]
    
    def return_values(self):
        return self.items,self.prices,self.summary


"""
import json

path = open('/Users/andybandela/Downloads/Screenshot 2024-02-26 at 14.59.32/analyzeExpenseResponse.json')
response = json.load(path)

def get_items(field):
    item = None
    price = None
    if "ValueDetection" in field:
        if str(field.get("Type")["Text"]) == "ITEM":
            item = str(field.get("ValueDetection")["Text"])
        elif str(field.get("Type")["Text"]) == "PRICE":
            price = field.get("ValueDetection")["Text"]
    return item, price
def get_summary(field):
    date = {}
    total = {}
    vendor = {}
    if "ValueDetection" in field:
        if str(field.get("Type")["Text"]) == "INVOICE_RECEIPT_DATE":
            date = {"date":field.get("ValueDetection")["Text"]}
            return date
        elif str(field.get("Type")["Text"]) == "TOTAL":
            total = {"total":field.get("ValueDetection")["Text"]}
            return total
        elif str(field.get("Type")["Text"]) == "VENDOR_NAME":
            if field.get("ValueDetection")["Confidence"] > 99.55:
                vendor = {"vendor":field.get("ValueDetection")["Text"]}
                return vendor



def update_fields(items,prices,summary,response):
    for expense_doc in response["ExpenseDocuments"]:
            for line_item_group in expense_doc["LineItemGroups"]:
                for line_items in line_item_group["LineItems"]:
                    for expense_fields in line_items["LineItemExpenseFields"]:
                        
                        item,price = get_items(expense_fields)
                        if item is not None:
                            items.append(item)
                        if price is not None:
                            prices.append(price)

            for summary_field in expense_doc["SummaryFields"]:
                temp = get_summary(summary_field)
                if temp is not None:
                    for t in temp:
                        summary[t] = temp[t]
           
items=[]
prices=[]
summary={}            
update_fields(items, prices, summary)            

print(prices,'\n',items)
print()
print(summary)
"""


    


