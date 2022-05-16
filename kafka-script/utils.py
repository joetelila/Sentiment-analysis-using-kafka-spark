# imports
from kafka import KafkaProducer
import time
import json
import tweepy
import config

# Twitter setup
# twitter setup
# Creating the authentication object
client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

# Creating the API instance
def json_serializer(data):
    return json.dumps(data, default=str).encode('utf-8')

# Create a producer
topic = "Elon_Musk_tweets"
# Searching for tweets about 'Elon Musk' which are not retweets and are in English
query = "Elon Musk -is:retweet lang:en"    #131.114.50.200 or localhost
#producer = KafkaProducer(bootstrap_servers='131.114.50.200:9092',value_serializer=json_serializer)

# Create a streamer
def get_twitter_data():
    response = client.search_recent_tweets(query=query,max_results=10, tweet_fields=['created_at','text','lang'], expansions=['author_id'], user_fields=['profile_image_url'])
    users = {u['id']: u for u in response.includes['users']}
    for tweet in response.data:
       if users[tweet.author_id]:
           user = users[tweet.author_id]
           print(user.profile_image_url)
           
           #result = {'created_at': tweet.created_at, 'text': tweet.text, 'tweet_id': tweet.id, 'username': user.username, 'profile_image_url': user.profile_image_url}
          # producer.send() - method uses fire-and-forget mode
          # .get() - method uses synchronous mode
           #producer.send(topic, result)
    print('10 tweets published to Kafka topic {}'.format(topic))
    print("-------------------------------------------\n")
       
# Start the stream
while True:
    get_twitter_data()
    time.sleep(5)
