import tweepy
import pandas as pd
from flask import Flask, render_template, request, logging, Response, redirect, flash
from config import CONFIG
# 各種ツイッターのキーをセット
CONSUMER_KEY = CONFIG["CONSUMER_KEY"]
CONSUMER_SECRET = CONFIG["CONSUMER_SECRET"]
ACCESS_TOKEN = CONFIG["ACCESS_TOKEN"]
ACCESS_SECRET = CONFIG["ACCESS_SECRET"]
#Tweepy
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
#APIインスタンスを作成
api = tweepy.API(auth)
# Flask の起動
app = Flask(__name__)
# Viewの処理
columns = [
   "tweet_id",
   "created_at",
   "text",
   "fav",
   "retweets"
   ]
@app.route('/', methods = ["GET" , "POST"])

def index():
   if request.method == 'POST':
       user_id = request.form['user_id']
       tweets_df = get_tweets_df(user_id)
       grouped_df = get_grouped_df(tweets_df)
       sorted_df = get_sorted_df(tweets_df)
       return render_template(
           'index.html',
           profile=get_profile(user_id),
           tweets_df = tweets_df,
           grouped_df = grouped_df,
           sorted_df = sorted_df
           )
   else:
       return render_template('index.html')

def get_tweets_df(user_id):
   tweets_df = pd.DataFrame(columns=columns) #1
   for tweet in tweepy.Cursor(api.user_timeline,screen_name = user_id, exclude_replies = True).items(): #2
       try:
           if not "RT @" in tweet.text: #3
               se = pd.Series([ #4
                       tweet.id,
                       tweet.created_at,
                       tweet.text.replace('\n',''),
                       tweet.favorite_count,
                       tweet.retweet_count
                   ]
                   ,columns
                   )
               tweets_df = tweets_df.append(se,ignore_index=True) #5
       except Exception as e:
           print (e)
   tweets_df["created_at"] = pd.to_datetime(tweets_df["created_at"]) #6
   return tweets_df #7

def get_profile(user_id):
   user = api.get_user(screen_name= user_id) #1
   profile = { #2
       "id": user.id,
       "user_id": user_id,
       "image": user.profile_image_url,
       "description": user.description # 自己紹介文の取得
   }
   return profile #3

def get_grouped_df(tweets_df):
   grouped_df = tweets_df.groupby(tweets_df.created_at.dt.date).sum().sort_values(by="created_at", ascending=False)
   return grouped_df

def get_sorted_df(tweets_df):
   sorted_df = tweets_df.sort_values(by="retweets", ascending=False)
   return sorted_df

if __name__ == '__main__':
  app.run(host="localhost")