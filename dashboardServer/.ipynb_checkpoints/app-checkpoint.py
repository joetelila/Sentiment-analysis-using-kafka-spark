'''
Title : Tweet sentiment Analysis using Apache Spark
        Dashboard web app.
Author : Yohannis K Telila
Date : 04 July 2022 

 command to run:
    $ flask run -h 131.114.50.200

'''

from flask import Flask, render_template, jsonify, request
import numpy as np
from datetime import datetime
import ast

application = Flask(__name__)

totalTweets = 0
posetiveTweets = 0
negativeTweets = 0
neutralTweets = 0
negative_tweets = []
user_handles = []

@application.route('/')
def homepage():
    return render_template("index.html",totalTweets=totalTweets,posetiveTweets=posetiveTweets,negativeTweets=negativeTweets,neutralTweets=neutralTweets)

@application.route('/updatetweetscount', methods=['POST'])
def updateT_count():
    global totalTweets, posetiveTweets, negativeTweets, neutralTweets
    return jsonify('',render_template('tweet_counts.html',totalTweets=totalTweets,posetiveTweets=posetiveTweets,negativeTweets=negativeTweets,neutralTweets=neutralTweets))

@application.route('/updatetweetspercent', methods=['POST'])
def updateT_percent():
    global totalTweets, posetiveTweets, negativeTweets, neutralTweets
    # try-catch - devision by 0 could occur.
    try:
        pos_percentage = np.round(posetiveTweets/totalTweets * 100, 2)
        neg_percentage = np.round(negativeTweets/totalTweets * 100, 2)
        neu_percentage = np.round(neutralTweets/totalTweets * 100, 2)
        return jsonify('',render_template('tweet_percentage.html',posetiveTweets=pos_percentage,negativeTweets=neg_percentage,neutralTweets=neu_percentage))
    except Exception as e:
        print("[ERROR]: ", e)
        return jsonify('',render_template('tweet_percentage.html',posetiveTweets=0,negativeTweets=0,neutralTweets=0))
        
@application.route('/updatedata', methods=['POST'])
def update_data():
    '''
    This route is called from the Spark context with data and update the local variable.
    '''
    global posetiveTweets, negativeTweets, neutralTweets, totalTweets
    
    #print recived data
    neutralTweets = ast.literal_eval(request.form['neutralTweet'])
    posetiveTweets = ast.literal_eval(request.form['posetiveTweet'])
    negativeTweets = ast.literal_eval(request.form['negativeTweet'])
    totalTweets = ast.literal_eval(request.form['totalTweet'])
    return "success",201

@application.route('/get_negative_tweet', methods=['POST'])
def get_negative_tweets():
    global negative_tweets
    if(len(negative_tweets) > 0):
        neg_tweet = negative_tweets.pop(0)
        created_at = neg_tweet['created_at']
        created_at = datetime.fromisoformat(created_at)
        created_at_ft = created_at.strftime("%B") +" "+ created_at.strftime("%d") +", "+ created_at.strftime("%H:%M")
        text = neg_tweet['text']
        username = neg_tweet['username']
        profile_image_url = neg_tweet['profile_image_url']
        return jsonify('',render_template('tweet_box.html',created_at=created_at_ft,text=text,username=username,profile_image_url=profile_image_url))
    # render the template here . . .
    return "success",201

@application.route('/add_negative_tweet', methods=['POST'])
def add_negative_tweets():
    global negative_tweets, user_handles
    content = request.json
    user_handle = content['username']
    if user_handle in user_handles:
        print("user already tweeted...")
    else:
        user_handles.append(user_handle)
        print("user never tweeted about Elon, added!")
        negative_tweets.append(content)
    return "success",201

if __name__ == "__main__":
   application.run()