# Serverless Computing Project
## Desciption
This is a Serverless clothes Sharing Website, which allows you to upload and give a desciption of your photos after you sign up and login to our website. You can search your photos by a specific key and you can also view all your posts. You can also list all the keys you upload and delete all items you upload. The user admin can delete all posts different users uploaded.In this project, I use the DynamoDB and S3 on AWS for my database and photo storage. I use zappa to delpoy my app onto AWS.And the most important thing is lambda function is running on the background to deal with deleting specific post or user. Also the lambda function will let the users receive an email from me after they signup using email as username.The lambda function is triggered by DynamoDB and S3.
## Getting started
### Installation
1. Set up virtual environment:
```
python3 -m venv venv  
source venv/bin/activate   
```
2. Install the required packages:
```
pip install -r requirements.txt  
```
3. Using zappa to deploy
```
zappa init
zappa deploy dev
```
if you want to debug
```
zappa tail
```
if you want to update your code
```
zappa update dev
```
## Display website
![alt text](https://github.com/margaretpell/Serverless_Computing_Project/blob/main/images/Screenshot%202023-04-12%20at%203.07.45%20PM.png)
1. authentication
![alt text](https://github.com/margaretpell/Serverless_Computing_Project/blob/main/images/Screenshot%202023-04-12%20at%203.07.54%20PM.png)
2. upload
![alt text](https://github.com/margaretpell/Serverless_Computing_Project/blob/main/images/Screenshot%202023-04-12%20at%203.08.26%20PM.png)
3. search
![alt text](https://github.com/margaretpell/Serverless_Computing_Project/blob/main/images/Screenshot%202023-04-12%20at%203.08.34%20PM.png)
![alt text](https://github.com/margaretpell/Serverless_Computing_Project/blob/main/images/Screenshot%202023-04-12%20at%203.10.06%20PM.png)
4. all keys
![alt text](https://github.com/margaretpell/Serverless_Computing_Project/blob/main/images/Screenshot%202023-04-12%20at%203.09.29%20PM.png)
5. all posts
![alt text](https://github.com/margaretpell/Serverless_Computing_Project/blob/main/images/Screenshot%202023-04-12%20at%203.09.21%20PM.png)



