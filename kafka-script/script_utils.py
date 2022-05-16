import requests
import json

sentiments = ["Neutral", "Positive", "Negative"]
sentiment_counts = {'Neutral':0, 'Positive':0, 'Negative':0}
# url for updating result.
url = 'http://localhost:5000/updatedata'

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
                        request_data = {'created_at': str(created_at), 'username': str(user_name), 'text': str(text), 'profile_image_url': str(profile_image_url)}
                        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                        response = requests.post(url_neg, data=json.dumps(request_data), headers=headers)
                        print(response.text) 