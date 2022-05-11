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
topic = "twitter_stream"
# Searching for tweets about 'Elon Musk' which are not retweets and are in English
query = "Elon Musk -is:retweet lang:en"    #131.114.50.200 or localhost
producer = KafkaProducer(bootstrap_servers='131.114.50.200:9092',value_serializer=json_serializer)

# Create a streamer
def get_twitter_data():
    response = client.search_recent_tweets(query=query,max_results=10, tweet_fields=['created_at','text','lang','author_id'])
    for tweet in response[0]:
       result = {'created_at': tweet.created_at, 'text': tweet.text, 'lang': tweet.lang, 'author_id': tweet.author_id}
       producer.send(topic, result)
    print('10 tweets published to Kafka topic {}'.format(topic))
    print("-------------------------------------------\n")

# Start the stream
while True:
    get_twitter_data()
    time.sleep(5)
