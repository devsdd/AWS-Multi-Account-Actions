# Add SNS trigger to this lambda and fire it on CLI with a command like:
# aws sns publish --topic-arn "arn:aws:sns:us-west-2:941837459948:test-topic" --message "Hello, World" --region us-west-2
# Increase lambda timeout to 15 min - done
# This works within 2 accounts - now have to replicate IAM roles in other accounts for it to work on all

import json
import boto3

def get_org_accounts():
    """retrieve list of all accounts in the organization"""
    client = boto3.client('organizations')
    response = client.list_accounts()

    accounts_list = []
    for row in response['Accounts']:
        accounts_list.append(row['Id'])
    
    return accounts_list
    

def assumed_role_session(role_arn: str):
    """switch to role in payee account"""
    role = boto3.client('sts').assume_role(RoleArn=role_arn, RoleSessionName='switch-role')
    credentials = role['Credentials']
    aws_access_key_id = credentials['AccessKeyId']
    aws_secret_access_key = credentials['SecretAccessKey']
    aws_session_token = credentials['SessionToken']
    return boto3.session.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token)

def refresh_TA_checks(boto3_client):
    """try to refresh all TA checks in account logged into"""
    # first run in main payer account
    # client = boto3.client('support', region_name = 'us-east-1')
    response = boto3_client.describe_trusted_advisor_checks(
        language='en'
    )
    
    check_IDs = []
    for check in response["checks"]:
        check_IDs.append(check["id"])

    for check in check_IDs:
        print(check)
        
    for check in check_IDs:
        try:
            response = boto3_client.refresh_trusted_advisor_check(checkId=check)
        except: # ignore individual check failures
            print("Unable to refresh check %s" % check)
        print(json.dumps(response, indent=4, sort_keys=True))

    response = boto3_client.describe_trusted_advisor_check_refresh_statuses(checkIds = check_IDs)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

def lambda_handler(event, context):
    
    accounts_list = [ "031704814400"]
    for account_ID in accounts_list:
        # current_role_arn = "arn:aws:iam::031704814400:role/TA-refresh-non-payer-role"
        current_role_arn = "arn:aws:iam::" + account_ID + ":role/TA-refresh-non-payer-role"
        # assumed_session = assumed_role_session(current_role_arn)
        # support_client = assumed_session.client('support', region_name = 'us-east-1')
        # response = refresh_TA_checks(support_client)
        # print(str(response))
    
    response = get_org_accounts()
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
