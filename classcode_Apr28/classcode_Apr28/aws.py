from flask import Flask, request

import uuid
import boto3

AWSKEY = 'PUT_YOUR_KEY_HERE'
AWSSECRET = 'PUT_YOUR_SECRET_HERE'
PUBLIC_BUCKET = 'PUT_YOUR_BUCKET_HERE'
STORAGE_URL = 'https://s3.amazonaws.com/' + PUBLIC_BUCKET + '/'

################################################################################
# S3 Stuff
################################################################################

def get_public_bucket():
    s3 = boto3.resource(service_name='s3',
                        region_name='us-east-1',
                        aws_access_key_id=AWSKEY,
                        aws_secret_access_key=AWSSECRET)
    bucket = s3.Bucket(PUBLIC_BUCKET)
    return bucket

def listfiles():
    bucket = get_public_bucket()
    items = []
    for item in bucket.objects.all():
        items.append(item.key)

    return { 'url':STORAGE_URL, 'items':items }


def uploadfile():
    bucket = get_public_bucket()
    file = request.files["file"]
    filename = file.filename
    # Hint for assignment 4: you can get other form elements like this: x = request.form.get('x')

    ct = 'image/jpeg'
    if filename.endswith('.png'):
        ct = 'image/png'

    filename = str(uuid.uuid4()) + '_' + filename

    bucket.upload_fileobj(file, filename, ExtraArgs={'ContentType':ct})

    return {'results':'OK'}


################################################################################
# DynamoDB Stuff
################################################################################

def get_table(name):
    dbclient = boto3.resource(service_name='dynamodb', region_name='us-east-1', aws_access_key_id=AWSKEY, aws_secret_access_key=AWSSECRET)
    return dbclient.Table(name)

def add_student(FirstName, LastName, Email):
    StudentID = str(uuid.uuid4())

    student = {
        'StudentID':StudentID,
        'FirstName':FirstName,
        'LastName':LastName,
        'Email':Email
    }
    table = get_table('Students')
    table.put_item(Item=student)

def list_students():
    table = get_table('Students')
    results = []
    for item in table.scan()['Items']:
        results.append(item)
    return results

def find_student(StudentID):
    table = get_table('Students')
    result = table.get_item(Key={'StudentID':StudentID})
    if 'Item' not in result:
        return None
    return result['Item']

def update_student(StudentID, Email):
    table = get_table('Students')
    table.update_item(
        Key={'StudentID':StudentID},
        UpdateExpression='set Email=:e',
        ExpressionAttributeValues={':e':Email}
    )

def delete_student(StudentID):
    table = get_table('Students')
    table.delete_item(Key={'StudentID':StudentID})


def add_remember_key(email):
    table = get_table('Remember')
    key = str(uuid.uuid4()) + str(uuid.uuid4())
    item = {'key':key, 'email':email}
    table.put_item(Item=item)
    return key












