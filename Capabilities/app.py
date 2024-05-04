from chalice import Chalice,Response, CognitoUserPoolAuthorizer
from chalicelib import storage_service
from chalicelib import textract_services
from chalicelib import dynamoDB_services
from chalicelib import cognito_services
import base64
import json
import os
import uuid
import re

app = Chalice(app_name='Capabilities')
_dir = os.path.dirname(__file__)

storage_location = "spendy-project"
storage_service = storage_service.StorageService(storage_location)
textract_services = textract_services.TextractService(storage_service)
dynamoDB_services = dynamoDB_services.Receipts()
cognito_services = cognito_services.CognitoService()
token_id = {}
user_sub = {}

authorizer = CognitoUserPoolAuthorizer('Spendy',provider_arns=['arn:aws:cognito-idp:us-east-1:#########:userpool/us-east-1_########'])

def render(tpl_path,context):
    path,filename = os.path.split(tpl_path)
    return

@app.route('/',methods=['GET'],cors = True)
def index():
    rel_path = "../Website/welcome.html"
    index = os.path.join(_dir,rel_path)
    
    with open(index,'r') as f:
        return Response(f.read(),status_code=200,headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})

@app.route('/token',methods=['POST'],cors = True)
def getToken():
    request_data = json.loads(app.current_request.raw_body)
    token = request_data['token']
    access = request_data['access']
    response = cognito_services.getUser(access)
    token_id['token'] = token
    token_id['access'] = access
    user_sub['sub']  = response['UserAttributes'][2]['Value']
    
    return token, access

@app.route('/home',methods=['GET'],cors=True,authorizer=authorizer)
def getIndex():
    rel_path = "../Website/insight.html"
    index = os.path.join(_dir,rel_path)
    with open(index,'r') as f:
        return Response(f.read(),status_code=200,headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})

@app.route('/upload', methods=['GET'], cors=True, authorizer=authorizer)
def upload():
    
    rel_path = "../Website/upload.html"
    index = os.path.join(_dir, rel_path)
    with open(index, 'r') as f:
        return Response(f.read(), status_code=200, headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})

    

@app.route('/images', methods = ['POST'], cors = True,authorizer=authorizer)
def upload_image():
    """processes file upload and saves file to storage service"""
    request_data = json.loads(app.current_request.raw_body)
    file_name = request_data['filename']
    file_bytes = base64.b64decode(request_data['filebytes'])
    

    image_info = storage_service.upload_file(file_bytes, file_name)
    print('Image Info: ',image_info)
    print()

    return image_info

@app.route('/analyse',methods = ['POST'], cors = True,authorizer=authorizer)
def analyz():
    request_data = json.loads(app.current_request.raw_body)
    file_name = request_data['filename']
    response = textract_services.analyse_receipt(file_name)
    
    print('image analysed')
    print(response)
    print()
    return response

@app.route('/add',methods = ['POST'],cors = True,authorizer=authorizer)
def add_receipt():
    request_data = json.loads(app.current_request.raw_body)
    receipt = request_data['receipt']
    #print('Test1')
    access_t = request_data['tkn']
    print('Access TKN')
    print(access_t)
    print('End')
   
    print('Access tkn')
    #print(access)
    print('End')
    user_info = cognito_services.getUser(access=access_t)
    print('Test2')
    sub = None
    id = uuid.uuid4()
    user_name = user_info['Username']
    email = None
    for attr in user_info['UserAttributes']:
        if attr['Name'] == 'email':
            email = attr['Value']
        if attr['Name'] == 'sub':
            sub = attr['Value']

    receipt['id'] = str(id)
    receipt['user_id'] = sub
    
    print()
    print('Receipt')
    print(receipt)
    response = dynamoDB_services.add_receipt(receipt)
    print('receipt added to table')
    print(response)
    print()
    for i in range (len(receipt['items'])):
        _id = uuid.uuid4()
        receipt['items'][i]['user_id'] = sub
        receipt['items'][i]['id'] = str(_id)
        dynamoDB_services.add_expense(receipt['items'][i])
        print('expense ',i)
        print(receipt['items'][i])
        print()
    
    return response

@app.route('/insight/{token}',methods=['GET'],cors=True,authorizer=authorizer)
def getInsight(token):

    #print(user_sub)
    #id = user_sub['sub']
    #print(id)
    print('Token - Insight')
    print(token)
    response = cognito_services.getUser(token)
    id = response['UserAttributes'][2]['Value']
    
    print()
    print('User id')
    print(id)

    print()
    item,total = dynamoDB_services.get_most_bought_item(id)
    #table_items = dynamoDB_services.get_all_rows(id)
    table_items = dynamoDB_services.get_all_rows1(id)
    print(table_items)
    response = {'item':item,'total':total,'table':table_items}
    print(response)
    return response

@app.route('/insights', methods=['GET'], cors=True, authorizer=authorizer)
def upload():
    
    rel_path = "../Website/insight.html"
    index = os.path.join(_dir, rel_path)
    with open(index, 'r') as f:
        return Response(f.read(), status_code=200, headers={"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"})
