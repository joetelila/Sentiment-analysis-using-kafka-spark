# importing the libraries
from pyspark.sql.session import SparkSession
from pyspark.sql.functions import col
# import structType
from pyspark.sql.types import StructType, StringType
from  pyspark.ml.pipeline import PipelineModel
from pyspark.sql.functions import from_json
from pyspark import SparkConf
import pyspark.sql.functions as F
from script_utils import *


conf = SparkConf()
conf.set("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1")
conf.set("spark.jars.packages", "com.johnsnowlabs.nlp:spark-nlp_2.12:3.4.4")
#3 executor per instance of each worker 
conf.set("spark.executor.memory", "6g")
# johnsnowlab nlp package
#spark_master = "spark://131.114.50.200:7077"
#spark_master = "spark://joetelila.local:7077"
spark_master = "spark://131.114.50.200:7079"
#spark_master = "spark://joetelila.lan:7077"
#spark_master = "spark://cpe-172-100-10-56.twcny.res.rr.com:7077"
#sc = pyspark.SparkContext(master=spark_master,appName="Hello Spark")
spark = SparkSession\
        .builder\
        .master(spark_master)\
        .appName("sentimentAnalysis_script")\
        .config(conf=conf)\
        .getOrCreate()

# show only errors.
spark._sc.setLogLevel("WARN")

# Loading model
print("[INFO] : Loading model...")
pipeline_model = PipelineModel.load('/home/y.telila/DEP/Sentiment-analysis-using-kafka-spark/pipeline_lr_js_model')
print("[INFO] : Model loaded successfully")
print("[INFO] : This model has accuracy of - 82%")

# set of kafka bootstrap servers, comma separated.
kafka_server = "131.114.50.200:9092"
#kafka_server = "localhost:9092"
# Subscribe to 1 topic
# Note : read how to config offsetsync !!!!!
#.option("startingOffsets", "latest") \
df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", kafka_server) \
  .option("subscribe", "ElonMusk") \
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
negative_tweets = pred_tweet.filter(pred_tweet.prediction == 2)
# Group (the count) tweets by prediction.
twt_pred = pred_tweet.groupBy('prediction').count()
twt_pred.printSchema()        
# write the output to console
# Every trigger(time), the sream will collect data from kafka and perform all 
# query and outputs to the sink(which is for_each_batch_function)
#  .trigger(processingTime="2 seconds") \
twt_pred = twt_pred.writeStream \
        .outputMode("update") \
        .foreachBatch(foreach_batch_function) \
        .option("truncate", "false") \
        .start()

# Every trigger(time), the sream will collect data from kafka and perform all 
# query and outputs to the sink(which is for_each_batch_function)
#  .trigger(processingTime="2 seconds") \
negative_tweets = negative_tweets.writeStream \
        .outputMode("append") \
        .foreachBatch(foreach_batch_neg_function) \
        .start()
twt_pred.awaitTermination()
negative_tweets.awaitTermination()