
import json
import requests
from os import environ
import boto3

queue_url=environ['queue_url']
open_search_url=environ['open_search_url']
user_name=environ['user_name']
password=environ['password']
index_name=environ['index_name']
db_table_name=environ['db_table_name']
gmail_id=environ['gmail_id']
open_search_auth=(user_name,password)


def get_message_from_queue():
    sqs = boto3.client('sqs')
    response = sqs.receive_message(QueueUrl=queue_url,MaxNumberOfMessages=1)
    if response.get('Messages'):
        message = response['Messages'][0]
        message_body = json.loads(message['Body'])
        receipt_handle = message['ReceiptHandle']

        sqs.delete_message(QueueUrl=queue_url,ReceiptHandle=receipt_handle)
        return {"type": 200, "body": message_body}
    else:
        return {"type": 400, "body": {}}



def fetch_restaurant_idx(cuisine):
    url = '%s/%s/_search' % (open_search_url, index_name)
    query = {
        'size': 5,
        'query': {
            'multi_match': {
                'query': cuisine,
                'fields': ['cuisine']
            }
        }
    }
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, auth=open_search_auth, headers=headers, data=json.dumps(query)).json()
    records = response['hits']['hits']
    return records

def create_message(restaurant_details,message):
    text="Hello There,\nHere are some restaurant suggestions for " + (message['body']['cuisine']).title() + " cuisines in "+ (message['body']['location']).title()
    text+="\nNumber of People:\t"+message['body']['numberofpeople']
    text+="\nTime:\t"+message['body']['time']
    for restaurant in restaurant_details:
        text+="\n\n"+restaurant['Item']['name']
        text+="\nAddress: "+ ",".join(restaurant['Item']['address'])
        text+="\nContact: "+ restaurant['Item']['contact']
        #url="https://maps.google.com/?q="+
        text+="\nLocation: https://maps.google.com/?q=%s,%s" %(restaurant['Item']['coordinates']['latitude'],restaurant['Item']['coordinates']['longitude'])
    
    return text
    
def get_restaurant_details(records):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(db_table_name)
    restaurant_details = []
    for record in records:
        r_id=record["_source"]["restaurant_id"]
        item=table.get_item(Key={'restaurant_id': r_id})
        restaurant_details.append(item)
    return restaurant_details
 
def send_email(id,message):
    ses_client = boto3.client("ses", region_name="us-east-1")
    response = ses_client.send_email(
        Source=gmail_id,
        Destination={
        'ToAddresses': [
            id,
            ],
         },
        Message={
            'Subject': {
                'Data': 'Restaurant Suggestions from the Dining Conceirge',
            },
            'Body': {
                'Text': {
                    'Data': message,
                },
            }
        },
    )
    print("Email Sent")
    
def lambda_handler(event,context):
    print(event)
    message=get_message_from_queue()
    if message['type'] == 200:
        #print(message)
        #return_text=message
        cuisine_type=message['body']['cuisine']
        records=fetch_restaurant_idx(cuisine_type)
        details=get_restaurant_details(records)
        mail_text=create_message(details,message)
        #print(mail_text)
        user_id=message['body']["email"]
        send_email(user_id,mail_text)
        return_text="Email Sent"
    else:
        return_text = "No Message in Queue"
    #print(return_text)
    return {
        'statusCode': 200,
        'body': return_text
    }
