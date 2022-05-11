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

# url for updating result.
sentiments = ["Neutral", "Positive", "Negative"]
sentiment_counts = {'Neutral':0, 'Positive':0, 'Negative':0}
url = 'http://localhost:5000/updatedata'


conf = SparkConf()
conf.set("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1")
                 
#spark_master = "spark://131.114.50.200:7077"
#spark_master = "spark://joetelila.local:7077"
spark_master = "spark://joetelila.lan:7077"
#sc = pyspark.SparkContext(master=spark_master,appName="Hello Spark")
spark = SparkSession\
        .builder\
        .master(spark_master)\
        .appName("sentimentAnalysis_script")\
        .config(conf=conf)\
        .getOrCreate()

# Loading model
print("[INFO] : Loading model...")
pipeline_model = PipelineModel.load('pipeline_lr_model')
print("[INFO] : Model loaded successfully")


kafka_server = "131.114.50.200:9092"
#kafka_server = "localhost:9092"
# Subscribe to 1 topic
df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", kafka_server) \
  .option("subscribe", "twitter_stream") \
  .option("startingOffsets", "latest") \
  .load()
df.printSchema()

# we are interested in the value column since it contains all the information from the kafka stream
# By default the value column is byte array, so we need to cast it to string format.
tweet_value = df.selectExpr("CAST(value AS STRING)")
tweet_schema = StructType() \
               .add("created_at", StringType())\
               .add("text", StringType()) \
               .add("lang", StringType()) \
                .add("author_id", StringType())

tweet_df = tweet_value.select(from_json(col("value"), tweet_schema).alias("tweet"))
tweet_df.printSchema()

# make a pridiction on each tweet of the stream
tweet_df = tweet_df.select("tweet.created_at", "tweet.text", "tweet.lang", "tweet.author_id")
tweet_df = tweet_df.withColumn('text', F.regexp_replace('text','@[A-Za-z0-9_]+',''))
tweet_df = tweet_df.withColumn('text', F.regexp_replace('text','https?://[^ ]+',''))
tweet_df = tweet_df.withColumn('text', F.regexp_replace('text','www.[^ ]+',''))
#tweet_df = pipelineFit.transform(tweet_df)
pred_tweet= pipeline_model.transform(tweet_df).select('author_id','text','probability','prediction')

# Group (the count) tweets by prediction. 
twt_pred = pred_tweet.groupBy('prediction').count()


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

        
# write the output to console
twt_pred.writeStream \
        .outputMode("update") \
        .trigger(processingTime="2 seconds") \
        .foreachBatch(foreach_batch_function) \
        .option("truncate", "false") \
        .start().awaitTermination()