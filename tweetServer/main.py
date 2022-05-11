from flask import Flask, render_template, jsonify, request
import numpy as np
import ast
application = Flask(__name__)

totalTweets = 0
posetiveTweets = 0
negativeTweets = 0
neutralTweets = 0

@application.route('/')
def homepage():
    return render_template("index.html",totalTweets=totalTweets,posetiveTweets=posetiveTweets,negativeTweets=negativeTweets,neutralTweets=neutralTweets)

@application.route('/updatetweetscount', methods=['POST'])
def updateT_count():
    global totalTweets, posetiveTweets, negativeTweets, neutralTweets
    return jsonify('',render_template('tweet_counts.html',totalTweets=totalTweets,posetiveTweets=posetiveTweets,negativeTweets=negativeTweets,neutralTweets=neutralTweets))

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

if __name__ == "__main__":
   application.run()