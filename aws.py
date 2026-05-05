import boto3
import os
from pathlib import Path

try:
	dotenv_module = __import__('dotenv')
	ENV_VARS = dotenv_module.dotenv_values(Path(__file__).resolve().parent / '.env')
except Exception:
	ENV_VARS = {}

AWS_ACCESS_KEY = ENV_VARS.get('AWS_ACCESS_KEY') or os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = ENV_VARS.get('AWS_SECRET_KEY') or os.getenv('AWS_SECRET_KEY')

USERS_TABLE = 'Users'


def get_table(name):
	dbclient = boto3.resource(
		service_name='dynamodb',
		region_name='us-east-1',
		aws_access_key_id=AWS_ACCESS_KEY,
		aws_secret_access_key=AWS_SECRET_KEY
	)
	return dbclient.Table(name)


def get_user_by_email(email):
	table = get_table(USERS_TABLE)
	result = table.get_item(Key={'email': email}) # Get item using the primary key (email)
	if 'Item' not in result:
		return None
	return result['Item']


def get_user_by_username(username):
	table = get_table(USERS_TABLE)
	items = table.scan().get('Items', [])
	for item in items:
		if item.get('username', '').lower() == username.lower(): # Get item by scanning the table and comparing the username (case-insensitive)
			return item
	return None


def signup_user(email, username, password):
	if get_user_by_email(email) is not None:
		return {'result': 'Email is already in use'}

	if get_user_by_username(username) is not None:
		return {'result': 'Username is already in use'}

	user = {
		'email': email,
		'username': username,
		'password': password,
		'photo': '' # Add the default user image with the URL of the image in S3
	}

	table = get_table(USERS_TABLE)
	table.put_item(Item=user)
	return {'result': 'OK', 'user': user}
