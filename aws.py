from flask import request
import boto3
import uuid
from datetime import datetime
from pathlib import Path
from dotenv import dotenv_values

ENV_VARS = dotenv_values(Path(__file__).resolve().parent / '.env')

AWS_ACCESS_KEY = ENV_VARS.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = ENV_VARS.get('AWS_SECRET_KEY') 

REGION = 'us-east-1'

USERS_TABLE = 'P5_Users'
ENTRIES_TABLE = 'P5_Blogs'


def table_handle(table_name):
    dynamo = boto3.resource(
        service_name='dynamodb',
        region_name=REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    return dynamo.Table(table_name)


def verify_login(email, password):
    users_table = table_handle(USERS_TABLE)
    lookup = users_table.get_item(Key={'email': email})
    if 'Item' not in lookup:
        return None

    account = lookup['Item']
    if account.get('password', '') != password:
        return None

    return account


def list_posts():
    posts_table = table_handle(ENTRIES_TABLE)
    posts = []

    rows = posts_table.scan().get('Items', [])
    for row in rows:
        posts.append(row)

    posts.sort(key=lambda row: row.get('date', ''), reverse=True)
    return posts


def add_post():
    title = request.args.get('title', '').strip()
    text = request.args.get('text', '').strip()

    if title == '':
        return {'result': 'Title cannot be blank'}
    if text == '':
        return {'result': 'Text cannot be blank'}

    post = {
        'entryID': str(uuid.uuid4()),
        'title': title,
        'text': text,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    posts_table = table_handle(ENTRIES_TABLE)
    posts_table.put_item(Item=post)
    return {'result': 'OK'}


def remove_post():
    post_id = request.args.get('id', '').strip()
    if post_id == '':
        return {'result': 'Entry id cannot be blank'}

    posts_table = table_handle(ENTRIES_TABLE)
    lookup = posts_table.get_item(Key={'entryID': post_id})
    if 'Item' not in lookup:
        return {'result': 'Entry not found'}

    posts_table.delete_item(Key={'entryID': post_id})
    return {'result': 'OK'}
