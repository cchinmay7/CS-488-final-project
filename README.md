# CS488 Final Project

A full-stack social media web application built with **Flask**, **JavaScript**, and **AWS** services including **DynamoDB** and **S3**. The project supports user authentication, profile pages, posting, replies, a personalized feed, and profile photo uploads.

## Overview

This project implements a lightweight social platform where users can:

- Create an account and log in with either email or username
- View their own profile and other users' profiles
- Create posts and reply to existing posts
- Browse a feed of recent posts from other users
- Upload a profile photo stored in Amazon S3

The backend is implemented in Python using Flask, while the frontend uses HTML templates, CSS, and client-side JavaScript. Persistent data is managed through Amazon DynamoDB.

## Features

- **User authentication**
  - Sign up with email, username, and password
  - Log in using email or username
  - Session-based authentication with Flask-Session

- **Profile management**
  - User profile pages
  - Separate rendering for a user's own profile vs. other users' profiles
  - Profile photo upload support

- **Posting system**
  - Create top-level posts
  - Reply to posts
  - View a post together with its replies

- **Social feed**
  - Displays recent posts from other users
  - Returns the 10 most recent feed posts

- **AWS integration**
  - **DynamoDB** for storing users and posts
  - **S3** for hosting uploaded profile images

## Tech Stack

- **Backend:** Python, Flask, Flask-Session
- **Frontend:** HTML, CSS, JavaScript
- **Cloud Services:** AWS DynamoDB, AWS S3
- **SDK / Libraries:** boto3, python-dotenv (optional for local environment loading)

## Project Structure

```text name=project-structure.txt
cs488-final-project/
├── aws.py                # AWS and data access layer
├── flask_app.py          # Flask routes and app logic
├── static/
│   ├── script.js         # Client-side interaction logic
│   └── styles.css        # Application styling
└── templates/
    ├── feed.html         # Feed page
    ├── login.html        # Login page
    ├── own_profile.html  # Logged-in user's profile page
    ├── reply.html        # Reply view/page
    ├── signup.html       # Signup page
    └── user_profile.html # Public view of another user's profile
```

## Application Architecture

### `flask_app.py`
Handles:
- Route definitions
- Session management
- Authentication checks
- Rendering HTML templates
- API-style endpoints for login, signup, profile data, posts, and uploads

### `aws.py`
Handles:
- DynamoDB table access
- User lookup and authentication
- Post creation and retrieval
- Feed generation
- Profile photo upload to S3

## Key Routes

### Pages
- `/final` — Landing page / signup redirect
- `/login.html` — Login page
- `/profile.html` — Redirect to the logged-in user’s profile
- `/feed.html` — Feed page
- `/reply.html?id=<postid>` — Reply page for a post
- `/u/<username>` — User profile page

### API Endpoints
- `/signup` — Create a user account
- `/login` — Authenticate a user
- `/logout` — Clear session
- `/profileinfo` — Retrieve user profile information
- `/userposts` — List posts for a given user
- `/feedposts` — List feed posts
- `/createpost` — Create a new post or reply
- `/post` — Get a single post and its replies
- `/uploadphoto` — Upload a profile photo

## Data Model

### Users table
Expected fields:
- `email`
- `username`
- `password`
- `photo`

### Posts table
Expected fields:
- `postid`
- `authorusername`
- `text`
- `createdat`
- `parentid`

## Setup Instructions

### 1. Clone the repository

```bash name=clone.sh
git clone https://github.com/cchinmay7/cs488-final-project.git
cd cs488-final-project
```

### 2. Create and activate a virtual environment

```bash name=venv.sh
python -m venv venv
source venv/bin/activate
```

On Windows:

```bash name=venv-windows.sh
venv\Scripts\activate
```

### 3. Install dependencies

```bash name=install.sh
pip install flask flask-session boto3 python-dotenv
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env name=.env.example
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
```

You should also ensure the following AWS resources exist:
- A DynamoDB table named `Users`
- A DynamoDB table named `Posts`
- An S3 bucket configured for public asset access

> Note: The current implementation references a specific bucket name in `aws.py`. Update that constant if you want to deploy the project under your own AWS account or infrastructure.

### 5. Run the Flask application

```bash name=run.sh
python flask_app.py
```

If needed, set the Flask entry point explicitly:

```bash name=run-flask.sh
export FLASK_APP=flask_app.py
flask run
```

## Example User Flow

1. A new user signs up with email, username, and password.
2. The application stores the user in DynamoDB.
3. The user logs in and a session is created.
4. The user is redirected to their profile page.
5. The user can create posts, reply to other posts, browse the feed, and upload a profile image.

## Current Limitations / Improvement Opportunities

- Passwords are stored in plain text and should be hashed before production use
- DynamoDB `scan()` is used in multiple places, which does not scale well for large datasets
- Bucket names and table names are hardcoded
- Input validation and error handling can be further strengthened
- No automated tests or deployment instructions are currently included

## Future Enhancements

- Password hashing and stronger authentication security
- Follow/friend relationships for a personalized feed
- Rich media posts and image attachments
- Pagination for posts and replies
- Better DynamoDB indexing and query patterns
- Deployment with environment-specific configuration

## License

No license has been specified for this repository.

## Author

Created by **cchinmay7** as a CS488 final project.
