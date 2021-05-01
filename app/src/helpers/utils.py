import string
import random
import pymongo
from app.src.helpers.database import mongo
from datetime import datetime
import timeago
def get_random_string(str_size=10):
    allowed_chars=string.ascii_letters + string.punctuation
    return ''.join(random.choice(allowed_chars) for x in range(str_size))

def get_user_documets(session):
    db_token=mongo.db.User_Tokens.find_one({
        'sessionHash': session['userToken']
    })
    userId=db_token['userId']
    uploaded_files=mongo.db.Files.find({
        'userId':userId,
        'isActive': True
    })
    formatted_data=[]
    for f in uploaded_files:
        formatted_data.append(f)
        timestamp=f['createdAt']
        t=str(datetime.utcnow())
        t,_ =t.split('.')

        timestamp=str(timestamp)
        timestamp,_ =timestamp.split('.')
        f['createdAt']=timeago.format(timestamp,t)
    return formatted_data

def get_user_info(session):
    db_token=mongo.db.User_Tokens.find_one({
        'sessionHash': session['userToken']
    })
    userId=db_token['userId']
    # print(userId)
    user_info=mongo.db.Users.find_one({
        '_id':userId
    })
    return user_info

def get_del_documets(session):
    db_token=mongo.db.User_Tokens.find_one({
        'sessionHash': session['userToken']
    })
    userId=db_token['userId']
    uploaded_files=mongo.db.Files.find({
        'userId':userId,
        'isActive': False
    })
    formatted_data=[]
    for f in uploaded_files:
        formatted_data.append(f)
        timestamp=f['createdAt']
        t=str(datetime.utcnow())
        t,_ =t.split('.')

        timestamp=str(timestamp)
        timestamp,_ =timestamp.split('.')
        f['createdAt']=timeago.format(timestamp,t)
    return formatted_data