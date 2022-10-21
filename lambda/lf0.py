import json
import boto3
import os

def lambda_handler(event, context):
    response = {}
    # Assign temporary userid if not provided
    if not event.get('userid'):
        event['userid'] = 'IAM_Temp_User'
    if event.get('messages'):
        client = boto3.client('lex-runtime')
        response = client.post_text(
        botAlias='Conciergetwo',
        botName='DiningConcierge',
        userId=event['userid'],
        sessionAttributes={},
        requestAttributes={},
        inputText=event['messages'][0]['unstructured']['text'])
        response =  {
            'statusCode': 200,
            'messages': [
                {
                    'type':'unstructured',
                    'unstructured':{
                        'text':response['message']
                    }
                }
            ]
        }
    else:
        response = {
            'statusCode': 400,
            'messages': [
                {
                    'type':'unstructured',
                    'unstructured':{
                        'text':'No message received'
                    }
                }
            ]
        }
        
    return response
