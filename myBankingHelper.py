import json
import random
import decimal
from re import A 

def random_num():
    return(decimal.Decimal(random.randrange(1000, 50000))/100)

def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']
    
def get_slot(intent_request, slotName):
    slots = get_slots(intent_request)
    if slots is not None and slotName in slots and slots[slotName] is not None:
        return slots[slotName]['value']['interpretedValue']
    else:
        return None    

def get_session_attributes(intent_request):
    sessionState = intent_request['sessionState']
    if 'sessionAttributes' in sessionState:
        return sessionState['sessionAttributes']

    return {}


def close(intent_request, session_attributes, fulfillment_state, message):
    intent_request['sessionState']['intent']['state'] = fulfillment_state
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': [message],
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }

accounts = {
    'Savings Account': {
        1000:{
            'bal':123.56,
            'dob':"2002-08-23"
        },
        1001:{
            'bal':54.15,
            "dob":'2001-05-04'
        },
        1002:{
            'bal':456.56,
            'dob':'1992-08-04'
        }
    },
    'Current Account': {
        2000:{
            'bal':411.0,
            'dob':"2001-08-23"
        },
        2001:{
            'bal':789.56,
            "dob":'2001-05-04'
        },
        2002:{
            'bal':456.56,
            'dob':'1992-08-04'
        }
    },
    'Fixed Deposit Account':{
        3000:{
            'bal':311.0,
            'dob':"2001-08-23"
        },
        3001:{
            'bal':789.56,
            "dob":'2001-05-04'
        },
        3002:{
            'bal':456.56,
            'dob':'1992-08-04'
        }
    },
    'Salary Account':{
        4000:{
            'bal':321.0,
            'dob':"2001-08-23"
        },
        4001:{
            'bal':789.56,
            "dob":'2001-05-04'
        },
        4002:{
            'bal':789,
            'dob':'1992-08-04'
        }
    }
    

}

accs = [1000,1001,1002,2000,2001,2002,3000,3001,3002,4000,4001,4002]
# InProgress

def CheckBalance(intent_request):
    session_attributes = get_session_attributes(intent_request)
    account = get_slot(intent_request, 'accountType')
    acc_number = get_slot(intent_request, 'accountNumber')
    acc_number = int(acc_number)
    dob = get_slot(intent_request, 'dateofBirth')


    if acc_number not in accs:
        text = 'Account not found. Please start from the beginning'
        message =  {
                'contentType': 'PlainText',
                'content': text
            }
        fulfillment_state = "InProgress"    
        return close(intent_request, session_attributes, fulfillment_state, message) 

    if dob == accounts[account][acc_number]['dob']:
        balance = str(accounts[account][int(acc_number)]['bal'])
        text = "Thank you. The balance on your "+account+" account is $"+balance+" dollars."
        message =  {
                'contentType': 'PlainText',
                'content': text
            }
        fulfillment_state = "Fulfilled"    
        return close(intent_request, session_attributes, fulfillment_state, message)   
    else:
        text = 'Date of birth is not matching with the one in the database. Please start from the beginning'
        message =  {
                'contentType': 'PlainText',
                'content': text
            }
        fulfillment_state = "InProgress"    
        return close(intent_request, session_attributes, fulfillment_state, message) 

def TransferFunds(intent_request):
    session_attributes = get_session_attributes(intent_request)
    acc_number = get_slot(intent_request, 'accountNumber')
    acc_number = int(acc_number)
    target_acc_number = get_slot(intent_request, 'targetAccountNumber')
    target_acc_number = int(target_acc_number)
    acc_type = get_slot(intent_request, 'accountType')
    target_acc_type = get_slot(intent_request, 'targetAccountType')
    transfer_amount = get_slot(intent_request, 'transferAmount')
    transfer_amount = float(transfer_amount)
    curr_bal = accounts[acc_type][acc_number]['bal']

    if curr_bal < transfer_amount:
        text = "Insufficient Amount. Please restart the transaction"
        message =  {
                'contentType': 'PlainText',
                'content': text
            }
        fulfillment_state = "Fulfilled"    
        return close(intent_request, session_attributes, fulfillment_state, message)
    
    if acc_number not in accs:
        text = 'Account not found. Please start from the beginning'
        message =  {
                'contentType': 'PlainText',
                'content': text
            }
        fulfillment_state = "InProgress"    
        return close(intent_request, session_attributes, fulfillment_state, message) 
    
    if target_acc_number not in accs:
        text = 'Beneficiary Account not found. Please start from the beginning'
        message =  {
                'contentType': 'PlainText',
                'content': text
            }
        fulfillment_state = "InProgress"    
        return close(intent_request, session_attributes, fulfillment_state, message) 


    accounts[acc_type][acc_number]['bal'] -= transfer_amount
    accounts[target_acc_type][target_acc_number]['bal'] += transfer_amount

    text = "Transaction Successful. The current balance on your account is $"+str(accounts[acc_type][acc_number]['bal'])+" dollars."
    message =  {
            'contentType': 'PlainText',
            'content': text
        }
    fulfillment_state = "Fulfilled"    
    return close(intent_request, session_attributes, fulfillment_state, message)
    
    
def dispatch(intent_request):
    intent_name = intent_request['sessionState']['intent']['name']
    response = None
    # Dispatch to your bot's intent handlers
    if intent_name == 'CheckBalance':
        return CheckBalance(intent_request)
    elif intent_name == 'TransferFunds':
        return TransferFunds(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def lambda_handler(event, context):
    response = dispatch(event)
    return response