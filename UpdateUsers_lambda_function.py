import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('players')

def lambda_handler(event, context):
    values = event['body']
    for i in range(10):
        oldV = table.get_item(Key={"id":str(i)})
        print(f'Items before update {oldV}')
        newV = values[i]
        table.update_item(Key={"id":str(i)}, ExpressionAttributeNames={"#skill":"skill", "#tier":"tier"}, 
        ExpressionAttributeValues={":S": newV['skill'],":T":newV['tier']}, 
        UpdateExpression="SET #skill = :S,#tier = :T")