from datetime import datetime
from flask import Blueprint, render_template, url_for, request, redirect, flash
from app import webapp
import base64
import boto3
from boto3.dynamodb.conditions import Key
from werkzeug.utils import secure_filename
import os
import random


main = Blueprint('main', __name__, static_folder="static",
                 template_folder="template")

bucket = webapp.config['S3BUCKET']
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')


class User:
    def __init__(self, username):
        self.username = None

current_user = User(None)

@main.route('/')
def index():
    return render_template("landing.html",user=current_user)

@main.route('/logout')
def logout():
    current_user.username = None
    return render_template("landing.html")

@main.route('/', methods=['GET'])
def landing():
    return render_template("landing.html", user=current_user)

@main.route('/list_keys', methods=['GET'])
def list_keys():
    try:
        table = dynamodb.Table('Posts')
        response = table.scan()
        items = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])
        posts = items
    except Exception as e:
        flash('Cannot query keys from dynamo db', 'error')
    return render_template("keys.html", posts=posts, user=current_user)

@main.route('/login',  methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        login_info = request.form
        username = login_info['username']
        password = login_info['password']

        try:
            table = dynamodb.Table('Users')
            response = table.query(
                KeyConditionExpression=Key('Username').eq(username)
            )
            items = response['Items']

            try:
                if items[0]['Password'] == password:
                    current_user.username = username
                    flash('you logged in', 'success')
                    return render_template("landing.html", user=current_user)
                else:
                    flash('login fail, wrong password', 'danger')
                    render_template("login.html")
            except:
                flash('login fail, no user found', 'danger')
        except:
            flash('user not found','danger')
    return render_template("login.html")

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        login_info = request.form
        username = login_info['username']
        password = login_info['password']
        try:
            if username and password:
                table = dynamodb.Table('Users')
                response = table.query(
                    KeyConditionExpression=Key('Username').eq(username)
                    )
                items = response['Items']
                if not items:
                    table.put_item(
                        Item={
                            'Username': username,
                            'Password': password
                        }
                    )
                    flash('Sign up successfully', 'success')
                    return render_template('login.html')
                else:
                    flash('Duplicate user name', 'danger')
                    return render_template("signup.html")
        except:
            return render_template("signup.html")
    return render_template("signup.html")

@main.route('/posts', methods=['GET'])
def posts():

    table = dynamodb.Table('Posts')
    response = table.scan()
    items = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])
    posts = items
    for post in posts:
        path = post['Image']
        data = s3_client.get_object(Bucket=bucket, Key=path)
        content = base64.b64encode(data['Body'].read()).decode('utf-8')
        post['Image'] = content
    return render_template("posts.html", posts=posts, user=current_user)

@main.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template("search.html", user=current_user)
    elif request.method == 'POST':
        key = request.form.get('key')
        if not key:
            flash('Please a key', 'danger')
            return render_template("search.html", user=current_user)
        try:

            table = dynamodb.Table('Posts')
            response = table.query(
                KeyConditionExpression=Key('Key').eq(key)
            )
            items = response['Items']
            if not items:
                flash('Key not found', 'danger')
                render_template("search.html", user=current_user)
            else:
                post = items[0]
                data = s3_client.get_object(Bucket=bucket, Key=post['Image'])
                content = base64.b64encode(data['Body'].read()).decode('utf-8')
                post['Image'] = content
                return render_template("post.html", post=post, user=current_user)
        except Exception as e:
            flash('Cannot retrieve the picture','danger')
        return render_template("search.html", user=current_user)

@main.route('/upload', methods=['GET', 'POST'])
def upload():

    if request.method == 'GET':
        return render_template("upload.html", user=current_user)
    elif request.method == "POST":
        file = request.files.get('file')
        username = current_user.username
        key = request.form.get('key')
        description = request.form.get('description')

        if not file or not key or not description:
            flash('Missing file, key or description','danger')
            return render_template("upload.html", user=current_user)

        filename = secure_filename(file.filename)
        file_name, file_ext = os.path.splitext(filename)


        # upload
        try:
            # define new path to be stored
            new_path = username + '/' + key + file_ext

            table = dynamodb.Table('Posts')
            response = table.query(
                KeyConditionExpression=Key('Key').eq(key)
            )

            if response['Items']:
                flash('Key exists, please enter a new key', 'danger')
                return render_template("upload.html", user=current_user)

            table.put_item(
                Item={
                    'Key': key,
                    'Username': username,
                    'Description': description,
                    'Image': new_path,
                    'Num_likes': 0
                }
            )
            # upload the image to s3
            s3_client.upload_fileobj(file, bucket, new_path)
            flash('the post is uploaded', 'success')
        except Exception as e:
            flash('failed uploading, try again please', 'danger')
        return render_template("upload.html", user=current_user)

@main.route('/delete_all', methods=['POST'])
def delete_all():

    try:
        # delete everything from dynamodb
        table = dynamodb.Table('Posts')
        scan = table.scan()
        with table.batch_writer() as batch:
            for each in scan['Items']:
                batch.delete_item(
                    Key={
                        'Key': each['Key']
                    }
                )
        # delete everything from s3
        s3_resource.Bucket(bucket).objects.all().delete()

        flash('Posts deleted', 'success')
        return render_template("landing.html", user=current_user)
    except:
        flash('Posts failed deleted', 'danger')
        return render_template("landing.html", user=current_user)

@main.route('/delete_post/<key>', methods=['POST'])
def delete_post(key):

    try:
        table = dynamodb.Table('Posts')
        response = table.query(
            KeyConditionExpression=Key('Key').eq(key)
        )
        items = response['Items']
        # get image file from s3
        if items:
            post = items[0]
            table.delete_item(Key={'Key': key})
            s3_client.delete_object(Bucket=bucket, Key=post['Image'])

        table = dynamodb.Table('Posts')

        response = table.query(
            IndexName='PostsByUsername',
            KeyConditionExpression=Key('Username').eq(current_user.username)
        )
        items = response['Items']
        if items:
            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response['Items'])
            posts = items
            for post in posts:
                path = post['Image']
                data = s3_client.get_object(Bucket=bucket, Key=path)
                content = base64.b64encode(data['Body'].read()).decode('utf-8')
                post['Image'] = content
            return render_template("my_posts.html", posts=posts, user=current_user)
        else:
            return render_template("my_posts.html", user=current_user)
    except:
        flash('error when deleting','danger')
        return render_template("landing.html", user=current_user)


@main.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'GET':
        return render_template("profile.html", user=current_user)
    elif request.method == "POST":
        new_password = request.form['password']
        try:
            table = dynamodb.Table('Users')
            print(current_user.username)
            response = table.update_item(
                Key={
                    'Username': current_user.username
                },
                UpdateExpression='SET Password = :value',
                ExpressionAttributeValues={
                    ':value': new_password
                }
            )
            print('updated')
            flash('Password Updated', 'success')
        except Exception as e:
            flash('Password did not get updated', 'danger')
        return render_template("profile.html", user=current_user)

@main.route('/my_posts', methods=['GET', 'POST'])
def my_posts():
    try:
        if request.method == 'GET':
            table = dynamodb.Table('Posts')

            response = table.query(
                IndexName='PostsByUsername',
                KeyConditionExpression=Key('Username').eq(current_user.username)
            )
            items = response['Items']
            if items:
                while 'LastEvaluatedKey' in response:
                    response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                    items.extend(response['Items'])
                posts = items
                for post in posts:
                    path = post['Image']
                    data = s3_client.get_object(Bucket=bucket, Key=path)
                    content = base64.b64encode(data['Body'].read()).decode('utf-8')
                    post['Image'] = content
                return render_template("my_posts.html", posts=posts, user=current_user)
            else:
                return render_template("my_posts.html", user=current_user)
    except:
        flash('error when showing your posts, you might need to login first','danger')
        return render_template("landing.html", user=current_user)
    return render_template("landing.html", user=current_user)