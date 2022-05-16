# importing the libraries
from pyspark.sql.session import SparkSession
from pyspark.sql.functions import col
# import structType
from pyspark.sql.types import StructType, StringType
from  pyspark.ml.pipeline import PipelineModel
from pyspark.sql.functions import from_json
from pyspark import SparkConf
import pyspark.sql.functions as F
import requests
import json


sentiments = ["Neutral", "Positive", "Negative"]
sentiment_counts = {'Neutral':0, 'Positive':0, 'Negative':0}
# url for updating result.
url = 'http://localhost:5000/updatedata'

conf = SparkConf()
conf.set("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1")
# johnsnowlab nlp package
#conf.set("spark.jars.packages", "com.johnsnowlabs.nlp:spark-nlp_2.12:3.4.4")
#spark_master = "spark://131.114.50.200:7077"
spark_master = "spark://joetelila.local:7077"
#spark_master = "spark://joetelila.lan:7077"
#spark_master = "spark://cpe-172-100-10-56.twcny.res.rr.com:7077"
#sc = pyspark.SparkContext(master=spark_master,appName="Hello Spark")
spark = SparkSession\
        .builder\
        .master(spark_master)\
        .appName("sentimentAnalysis_script")\
        .config(conf=conf)\
        .getOrCreate()

def prepare_request_data(data_dict):
        global sentiment_counts, sentiments
        for key, value in data_dict.items():
                sentiment_counts[sentiments[int(key)]] = int(value)
        totalTweets = sum(sentiment_counts.values())
        request_data = {'totalTweet': str(totalTweets), 'posetiveTweet': str(sentiment_counts["Positive"]), 'negativeTweet': str(sentiment_counts["Negative"]), 'neutralTweet': str(sentiment_counts["Neutral"])}
        return request_data 

def foreach_batch_function(df, epoch_id):
        print("[INFO] : Batch {}".format(epoch_id))
        # store the value of the count on the variable
        '''
           - toPandas():
                 This method should only be used if the resulting Pandas’s 
                 DataFrame is expected to be small, as all the data is loaded 
                 into the driver’s memory.
        '''
        panda_df = df.toPandas()
        request_data = prepare_request_data(dict(panda_df.values))
        # try catch
        try:
                response = requests.post(url, data=request_data)
                print(response.text)
        except Exception as e:
                print(e)

def foreach_batch_neg_function(df, epoch_id):
        print("[INFO][NEG] : Batch {}".format(epoch_id))
        # store the value of the count on the variable
        '''
           - toPandas():
                 This method should only be used if the resulting Pandas’s 
                 DataFrame is expected to be small, as all the data is loaded 
                 into the driver’s memory.
        '''
        panda_df = df.select("created_at","text","profile_image_url","username").limit(2).toPandas()
        if len(panda_df) > 0:
                tweetsList = panda_df.values.tolist()
                url_neg = 'http://localhost:5000/add_negative_tweet'
                for tweet in tweetsList:
                        created_at = tweet[0]
                        text = tweet[1]
                        profile_image_url = tweet[2]
                        user_name = tweet[3]
                        request_data = {'created_at': str(created_at), 'username': str('@'+str(user_name)), 'text': str(text), 'profile_image_url': str(profile_image_url)}
                        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                        response = requests.post(url_neg, data=json.dumps(request_data), headers=headers)
                        print(response.text) 
# Loading model
print("[INFO] : Loading model...")
pipeline_model = PipelineModel.load('pipeline_lr_model')
print("[INFO] : Model loaded successfully")
print("[INFO] : This model has accuracy of - 60%, HODL on better model is training . . .")

# set of kafka bootstrap servers, comma separated.
kafka_server = "131.114.50.200:9092"
#kafka_server = "localhost:9092"
# Subscribe to 1 topic
# Note : read how to config offsetsync !!!!!
df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", kafka_server) \
  .option("subscribe", "Elon_Musk_tweets") \
  .option("startingOffsets", "latest") \
  .load()
df.printSchema()
'''
root
 |-- key: binary (nullable = true)
 |-- value: binary (nullable = true)
 |-- topic: string (nullable = true)
 |-- partition: integer (nullable = true)
 |-- offset: long (nullable = true)
 |-- timestamp: timestamp (nullable = true)
 |-- timestampType: integer (nullable = true)
'''
# we are interested in the value column since it contains all the information from the kafka stream
# By default the value column is byte array, so we need to cast it to string format.
tweet_value = df.selectExpr("CAST(value AS STRING)")
tweet_schema = StructType() \
               .add("created_at", StringType())\
               .add("text", StringType()) \
               .add("tweet_id", StringType()) \
               .add("username", StringType()) \
               .add("profile_image_url", StringType())

tweet_df = tweet_value.select(from_json(col("value"), tweet_schema).alias("tweet"))
tweet_df.printSchema()
'''
root
 |-- tweet: struct (nullable = true)
 |    |-- created_at: string (nullable = true)
 |    |-- text: string (nullable = true)
 |    |-- lang: string (nullable = true)
 |    |-- author_id: string (nullable = true)
'''
# cleaning up tweets
tweet_df = tweet_df.select("tweet.created_at", "tweet.text", "tweet.tweet_id", "tweet.username", "tweet.profile_image_url")
tweet_df.printSchema()
'''
root
 |-- created_at: string (nullable = true)
 |-- text: string (nullable = true)
 |-- lang: string (nullable = true)
 |-- author_id: string (nullable = true)
'''
# remove handle from the tweets
tweet_df = tweet_df.withColumn('text', F.regexp_replace('text','@[A-Za-z0-9_]+',''))
# remove links from the tweets
tweet_df = tweet_df.withColumn('text', F.regexp_replace('text','https?://[^ ]+',''))
tweet_df = tweet_df.withColumn('text', F.regexp_replace('text','www.[^ ]+',''))

#tweet_df = pipelineFit.transform(tweet_df)
pred_tweet= pipeline_model.transform(tweet_df)
negative_tweets = pred_tweet.filter(pred_tweet.prediction == 0)
# Group (the count) tweets by prediction.
twt_pred = pred_tweet.groupBy('prediction').count()
twt_pred.printSchema()        
# write the output to console
twt_pred = twt_pred.writeStream \
        .outputMode("update") \
        .trigger(processingTime="2 seconds") \
        .foreachBatch(foreach_batch_function) \
        .option("truncate", "false") \
        .start()
negative_tweets = negative_tweets.writeStream \
        .outputMode("append") \
        .trigger(processingTime="2 seconds") \
        .option("truncate", "true") \
        .foreachBatch(foreach_batch_neg_function) \
        .start()
twt_pred.awaitTermination()
negative_tweets.awaitTermination()