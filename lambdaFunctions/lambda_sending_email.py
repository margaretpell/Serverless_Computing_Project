import boto3

# Create a Boto3 client for SES and DynamoDB
dynamo_client = boto3.client('dynamodb')
ses_client = boto3.client('ses')


def lambda_handler(event, context):
    # Get the username (which is the email address) from the event
    username = event['Records'][0]['dynamodb']['Keys']['Username']['S']
    print(username)

    # Check if the user already exists in the "Users" table
    response = dynamo_client.get_item(
        TableName='Users',
        Key={
            'Username': {'S': username}
        },
        ProjectionExpression='Email'
    )

    # If the user does not exist, send a welcome message to their email
    if 'Item' not in response:
        # Get the email address associated with the username from the "Users" table
        email = username

        # Send a welcome message to the user's email address using Amazon SES
        response = ses_client.send_email(
            Source='',
            Destination={
                'ToAddresses': [email]
            },
            Message={
                'Subject': {
                    'Data': 'Welcome to our Women Sharing Community App!'
                },
                'Body': {
                    'Text': {
                        'Data': f'Welcome to our Women Sharing Community App, {username}! Here you will get the latest fashion news!'
                    }
                }
            }
        )

    # Return a success message
    return {
        'statusCode': 200,
        'body': 'Welcome message sent!'
    }

