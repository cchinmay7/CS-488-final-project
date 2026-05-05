from flask import Flask, request, render_template, session, redirect
from flask_session import Session

import aws

app = Flask(__name__)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


def is_logged_in():
	if session.get('email') is None:
		return False
	if session.get('username') is None:
		return False
	return True

@app.route('/final')
def final():
	if is_logged_in():
		return redirect('/u/' + session['username'])
	return render_template('signup.html')


@app.route('/login.html')
def login_html():
	if is_logged_in():
		return redirect('/u/' + session['username'])
	return render_template('login.html')


@app.route('/signup')
def signup():
	email = request.args.get('email', '').strip()
	username = request.args.get('username', '').strip()
	password = request.args.get('password', '').strip()

	if email == '':
		return {'result': 'Email cannot be blank'}

	if '@' not in email or '.' not in email:
		return {'result': 'Email must include @ and .'}

	if username == '':
		return {'result': 'UserName cannot be blank'}

	if password == '':
		return {'result': 'Password cannot be blank'}

	result = aws.signup_user(email, username, password)
	if result['result'] != 'OK':
		return {'result': result['result']}

	user = result['user']
	session['email'] = user['email']
	session['username'] = user['username']
	return {'result': 'OK', 'username': user['username']}

@app.route('/login')
def login():
	login_value = request.args.get('login', '').strip()
	password = request.args.get('password', '').strip()

	if login_value == '':
		return {'result': 'Email or UserName cannot be blank'}

	if password == '':
		return {'result': 'Password cannot be blank'}

	result = aws.login_user(login_value, password)
	if result['result'] != 'OK':
		return {'result': result['result']}

	user = result['user']
	session['email'] = user['email']
	session['username'] = user['username']
	return {'result': 'OK', 'username': user['username']}

@app.route('/logout')
def logout():
	session.pop('email', None)
	session.pop('username', None)
	return {'result': 'OK'}

@app.route('/logout.html')
def logout_html():
	session.pop('email', None)
	session.pop('username', None)
	return redirect('/login.html')


# /////////////////////////////////////////////////////////////////////////////


@app.route('/u/<username>')
def profile_html(username):
	if not is_logged_in():
		return redirect('/login.html')
	if username.lower() == session['username'].lower():
		return render_template('own_profile.html', username=username)
	return render_template('user_profile.html', username=username)


@app.route('/reply.html')
def reply_html():
	if not is_logged_in():
		return redirect('/login.html')

	postid = request.args.get('id', '').strip()
	if postid == '':
		return redirect('/u/' + session['username'])

	return render_template('reply.html', postid=postid)


@app.route('/profileinfo')
def profileinfo():
	if not is_logged_in():
		return {'result': 'You must be logged in'}

	username = request.args.get('username', '').strip()
	if username == '':
		return {'result': 'UserName cannot be blank'}

	return aws.get_profile_info(username, session['username'])


@app.route('/userposts')
def userposts():
	if not is_logged_in():
		return {'result': 'You must be logged in'}

	username = request.args.get('username', '').strip()
	if username == '':
		return {'result': 'UserName cannot be blank'}

	return aws.list_user_posts(username)


@app.route('/createpost')
def createpost():
	if not is_logged_in():
		return {'result': 'You must be logged in'}

	text = request.args.get('text', '').strip()
	parent = request.args.get('parent', '').strip()

	if text == '':
		return {'result': 'Post text cannot be blank'}

	if parent == '':
		parent = ''

	return aws.create_post(session['username'], text, parent)


@app.route('/post')
def post():
	if not is_logged_in():
		return {'result': 'You must be logged in'}

	postid = request.args.get('id', '').strip()
	if postid == '':
		return {'result': 'Post ID cannot be blank'}

	return aws.get_post_and_replies(postid)


# /////////////////////////////////////////////////////////////////////////////


@app.route('/uploadphoto', methods=['POST'])
def uploadphoto():
	if not is_logged_in():
		return {'result': 'You must be logged in'}

	if 'file' not in request.files:
		return {'result': 'Please choose a file'}

	file = request.files['file']
	return aws.upload_profile_photo(session['email'], file)

