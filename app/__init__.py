from flask import Flask
from app.config import Config
import boto3
from flask_bootstrap import Bootstrap

webapp = Flask(__name__, static_folder='static')
webapp.config.from_object(Config)
bootstrap = Bootstrap(webapp)
# create table in dynamodb
dynamodb = boto3.resource('dynamodb')

try:
    usertable = dynamodb.create_table(
        TableName='Users',
        KeySchema=[
            {
                'AttributeName': 'Username',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'Username',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    # Wait until the table exists.
    usertable.meta.client.get_waiter('table_exists').wait(TableName='Users')
except Exception as e:
    webapp.logger.error(e)

try:
    posttable = dynamodb.create_table(
        TableName='Posts',
        KeySchema=[
            {
                'AttributeName': 'Key',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'Key',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'Username',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        },
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'PostsByUsername',
                'KeySchema': [
                    {
                        'AttributeName': 'Username',
                        'KeyType': 'HASH'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            },
        ]
    )
    # Wait until the table exists.
    posttable.meta.client.get_waiter('table_exists').wait(TableName='Posts')
except Exception as e:
    webapp.logger.error(e)



from app.main import main

from pytz import timezone

eastern = timezone('US/Eastern')

webapp.register_blueprint(main, url_prefix='')
