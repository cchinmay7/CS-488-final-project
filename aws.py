import boto3
import uuid
from datetime import datetime
from pathlib import Path
from dotenv import dotenv_values

ENV_VARS = dotenv_values(Path(__file__).resolve().parent / '.env')

AWS_ACCESS_KEY = ENV_VARS.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = ENV_VARS.get('AWS_SECRET_KEY')

REGION = 'us-east-1'
DEFAULT_PHOTO_URL = '/static/default-profile.svg'

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


def get_user_by_email(email):
    users_table = table_handle(USERS_TABLE)
    lookup = users_table.get_item(Key={'email': email})
    if 'Item' not in lookup:
        return None
    return lookup['Item']


def get_user_by_username(username):
    users_table = table_handle(USERS_TABLE)
    rows = users_table.scan().get('Items', [])
    for row in rows:
        if row.get('username', '').lower() == username.lower():
            return row
    return None


def signup_user(email, username, password):
    if get_user_by_email(email) is not None:
        return {'result': 'Email is already in use'}

    if get_user_by_username(username) is not None:
        return {'result': 'Username is already in use'}

    account = {
        'email': email,
        'username': username,
        'password': password,
        'photo': DEFAULT_PHOTO_URL
    }
    users_table = table_handle(USERS_TABLE)
    users_table.put_item(Item=account)
    return {'result': 'OK', 'user': account}


def verify_login(login_id, password):
    account = get_user_by_email(login_id)
    if account is None:
        account = get_user_by_username(login_id)

    if account is None:
        return None

    if account.get('password', '') != password:
        return None

    if account.get('photo', '') == '':
        account['photo'] = DEFAULT_PHOTO_URL

    return account


def update_photo(email, photo_url):
    users_table = table_handle(USERS_TABLE)
    users_table.update_item(
        Key={'email': email},
        UpdateExpression='set photo=:p',
        ExpressionAttributeValues={':p': photo_url}
    )


def add_post(author_email, author_username, text, parent_id=''):
    if text.strip() == '':
        return {'result': 'Post text cannot be blank'}

    post = {
        'entryID': str(uuid.uuid4()),
        'authorEmail': author_email,
        'authorUsername': author_username,
        'text': text.strip(),
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'parentID': parent_id
    }

    posts_table = table_handle(ENTRIES_TABLE)
    posts_table.put_item(Item=post)
    return {'result': 'OK', 'entryID': post['entryID']}


def get_post(entry_id):
    posts_table = table_handle(ENTRIES_TABLE)
    lookup = posts_table.get_item(Key={'entryID': entry_id})
    if 'Item' not in lookup:
        return None
    return lookup['Item']


def list_recent_posts(limit_count=10):
    posts_table = table_handle(ENTRIES_TABLE)
    rows = posts_table.scan().get('Items', [])

    posts = []
    for row in rows:
        if row.get('parentID', '') == '':
            posts.append(row)

    posts.sort(key=lambda row: row.get('date', ''), reverse=True)
    return posts[:limit_count]


def list_posts_by_username(username):
    posts_table = table_handle(ENTRIES_TABLE)
    rows = posts_table.scan().get('Items', [])

    posts = []
    for row in rows:
        if row.get('parentID', '') == '' and row.get('authorUsername', '').lower() == username.lower():
            posts.append(row)

    posts.sort(key=lambda row: row.get('date', ''), reverse=True)
    return posts


def list_replies(parent_id):
    posts_table = table_handle(ENTRIES_TABLE)
    rows = posts_table.scan().get('Items', [])

    replies = []
    for row in rows:
        if row.get('parentID', '') == parent_id:
            replies.append(row)

    replies.sort(key=lambda row: row.get('date', ''), reverse=False)
    return replies
