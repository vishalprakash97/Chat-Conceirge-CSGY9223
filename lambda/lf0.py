
import json

def lambda_handler(event, context):
    # TODO implement
    response =  {
        'statusCode': 200,
        'userid':event['userid'],
        'messages': [
                {
                    'type':'unstructured',
                    'unstructured':{
                        'text': 'Application under development. Search functionality will be implemented in Assignment 2'
                    }
                }
            ]
        }
    return response