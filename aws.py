import boto3
import os
import uuid
import datetime
from pathlib import Path

try:
	dotenv_module = __import__('dotenv')
	ENV_VARS = dotenv_module.dotenv_values(Path(__file__).resolve().parent / '.env')
except Exception:
	ENV_VARS = {}

AWS_ACCESS_KEY = ENV_VARS.get('AWS_ACCESS_KEY') or os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = ENV_VARS.get('AWS_SECRET_KEY') or os.getenv('AWS_SECRET_KEY')
PUBLIC_BUCKET = 'cc55048n-bucket'
STORAGE_URL = 'https://' + PUBLIC_BUCKET + '.s3.us-east-1.amazonaws.com/'

USERS_TABLE = 'Users'
POSTS_TABLE = 'Posts'
DEFAULT_PHOTO_URL = 'https://cc55048n-bucket.s3.us-east-1.amazonaws.com/generic.png'


def get_table(name):
	dbclient = boto3.resource(
		service_name='dynamodb',
		region_name='us-east-1',
		aws_access_key_id=AWS_ACCESS_KEY,
		aws_secret_access_key=AWS_SECRET_KEY
	)
	return dbclient.Table(name)


def get_public_bucket():
	s3 = boto3.resource(
		service_name='s3',
		region_name='us-east-1',
		aws_access_key_id=AWS_ACCESS_KEY,
		aws_secret_access_key=AWS_SECRET_KEY
	)
	return s3.Bucket(PUBLIC_BUCKET)


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

def login_user(login_value, password):
	if '@' in login_value:
		user = get_user_by_email(login_value)
	else:
		user = get_user_by_username(login_value)

	if user is None:
		return {'result': 'Account not found'}

	if user.get('password', '') != password:
		return {'result': 'Password is incorrect'}

	return {'result': 'OK', 'user': user}


# /////////////////////////////////////////////////////////////////////////////


def get_profile_info(username):
	user = get_user_by_username(username)
	if user is None:
		return {'result': 'User not found'}

	photo = user.get('photo', '')
	if photo == '':
		photo = DEFAULT_PHOTO_URL

	return {
		'result': 'OK',
		'username': user['username'],
		'photo': photo
	}


def create_post(author_username, text, parent_id):
	post = {
		'postid': str(uuid.uuid4()),
		'authorusername': author_username,
		'text': text,
		'createdat': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
		'parentid': parent_id
	}

	table = get_table(POSTS_TABLE)
	table.put_item(Item=post)
	return {'result': 'OK', 'post': post}


def list_user_posts(username):
	table = get_table(POSTS_TABLE)
	results = []
	items = table.scan().get('Items', [])

	for item in items:
		if item.get('parentid', '') != '':
			continue
		if item.get('authorusername', '').lower() != username.lower():
			continue
		results.append(item)

	results.sort(key=lambda x: x.get('createdat', ''), reverse=True)
	return {'result': 'OK', 'posts': results}


def list_feed_posts(exclude_username):
	table = get_table(POSTS_TABLE)
	results = []
	items = table.scan().get('Items', [])

	for item in items:
		if item.get('parentid', '') != '':
			continue
		if item.get('authorusername', '').lower() == exclude_username.lower():
			continue
		results.append(item)

	results.sort(key=lambda x: x.get('createdat', ''), reverse=True)
	if len(results) > 10:
		results = results[:10]
	return {'result': 'OK', 'posts': results}


def get_post_and_replies(postid):
	table = get_table(POSTS_TABLE)
	items = table.scan().get('Items', [])

	main_post = None
	replies = []

	for item in items:
		if item.get('postid', '') == postid:
			main_post = item
			continue

		if item.get('parentid', '') == postid:
			replies.append(item)

	if main_post is None:
		return {'result': 'Post not found'}

	replies.sort(key=lambda x: x.get('createdat', ''))
	return {'result': 'OK', 'post': main_post, 'replies': replies}


# /////////////////////////////////////////////////////////////////////////////


def upload_profile_photo(email, file):
	filename = file.filename
	if filename == '':
		return {'result': 'Please choose a file'}

	ct = 'image/jpeg'
	if filename.lower().endswith('.png'):
		ct = 'image/png'

	new_filename = str(uuid.uuid4()) + '_' + filename
	bucket = get_public_bucket()
	bucket.upload_fileobj(file, new_filename, ExtraArgs={'ContentType': ct})

	photo_url = STORAGE_URL + new_filename
	table = get_table(USERS_TABLE)
	table.update_item(
		Key={'email': email},
		UpdateExpression='set photo=:p',
		ExpressionAttributeValues={':p': photo_url}
	)

	return {'result': 'OK', 'url': photo_url}
