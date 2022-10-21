import json
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

sqs = boto3.client('sqs')

def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }
    
def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response
    
def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

def build_validation_result(is_valid, violated_slot, message_content):
    '''if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }'''

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def validate_data(location, cuisine, time, numberofpeople, phonenumber, email): #added email
    #response = {"status": 200, "message": ""}
    
    if location is not None:
        if location.lower() not in ['new york', 'nyc', 'new york city', 'brooklyn', 'manhattan', 'bronx',
                                         'staten island', 'queens']:
                return build_validation_result(False,
                                       'location',
                                       'Sorry, we only serve in New York City')
    
    if cuisine is not None:
        if cuisine.lower() not in ['indian', 'italian', 'chinese', 'japanese', 'mediterranean', 'thai']:
                return build_validation_result(False,
                                       'cuisine',
                                       'Sorry, available cuisines are Indian, Italian, Chinese, Japanese, Mediterranean and Thai')
    
    if time is not None:
        if len(time) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'time', 'Error!')

        hour, minute = time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'time', 'Error!')

        '''if hour < 10 or hour > 16:
            # Outside of business hours
            return build_validation_result(False, 'time', 'Our business hours are from ten a m. to five p m. Can you specify a time during this range?')'''
    
    if numberofpeople is not None:
        if int(numberofpeople) not in range(1, 21):
            #response = {"status": 400, "message": "Number of people should be between 1 and 20"}
            return build_validation_result(False,
                                       'numberofpeople',
                                       'Number of people should be between 1 and 20')
                                       
    #if phonenumber is not None:
    return build_validation_result(True, None, None)
    
def get_slots(intent_request):
    return intent_request['currentIntent']['slots']
    

def GetRestaurantDetails(intent_request):
    location = get_slots(intent_request)["location"]
    cuisine = get_slots(intent_request)["cuisine"]
    time = get_slots(intent_request)["time"]
    numberofpeople = get_slots(intent_request)["numberofpeople"]
    phonenumber = get_slots(intent_request)["phonenumber"]
    email = get_slots(intent_request)["email"] #added email
    source = intent_request['invocationSource']
    
    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)

        validation_result = validate_data(location, cuisine, time, numberofpeople, phonenumber, email) #added email
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        # Pass the price of the flowers back through session attributes to be used in various prompts defined
        # on the bot model.
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        '''if flower_type is not None:
            output_session_attributes['Price'] = len(flower_type) * 5  # Elegant pricing model'''

        return delegate(output_session_attributes, get_slots(intent_request))
        
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Thank you for the information! We will send a confirmation email to you shortly.'})

def dispatch(intent_request):
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'GetRestaurantDetails':
        return GetRestaurantDetails(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def send_message_to_SQS(slots):
    msg = {
        'location': slots['location'],
        'cuisine': slots['cuisine'],
        'time': slots['time'],
        'numberofpeople': slots['numberofpeople'],
        'phonenumber': slots['phonenumber'],
        'email': slots['email'] #added email
    }
    
    '''msg = {
        'test': slots['dialogAction']['type'],
        'location': slots['dialogAction']['slots']
    }'''

    response = sqs.send_message(
        QueueUrl="https://sqs.us-east-1.amazonaws.com/019281413155/RestaurantQueryQueue.fifo",
        DelaySeconds=0,
        MessageBody=json.dumps(msg),
        MessageGroupId='LF1'
    )

def lambda_handler(event, context):
    # TODO implement
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    
    response = dispatch(event)
    
    if event['currentIntent']['slots']['email']:
        send_message_to_SQS(event['currentIntent']['slots'])
        #send_message_to_SQS(response)

    return response
