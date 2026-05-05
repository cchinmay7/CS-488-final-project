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
    return render_template('signup.html')

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
	return {'result': 'OK'}

