import json
import datetime
import boto3
import decimal
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')


def lambda_handler(event, context):
    
    table = dynamodb.Table('players')
    
    TableScan = table.scan()
    
    return {
        'statusCode': 200,
        'body': json.dumps(TableScan, cls = JsonDecimalToInt)
    }


class JsonDecimalToInt(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(JsonDecimalToInt, self).default(obj)