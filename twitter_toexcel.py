import tweepy
import pandas as pd
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import streamlit as st


consumer_key = st.secrets["consumer_key"]
consumer_secret = st.secrets["consumer_secret"]
access_token = st.secrets["access_token"]
access_token_secret = st.secrets["access_token_secret"]
auth = tweepy.OAuth1UserHandler(
   consumer_key, consumer_secret, access_token, access_token_secret
)
api = tweepy.API(auth)

# tweet = api.get_status(1546888044711743488)
# tweet.
# print(tweet.text)

def update_urls(tweet, api, urls):
    tweet_id = tweet.id
    user_name = tweet.user.screen_name
    max_id = None
    replies = tweepy.Cursor(api.search_tweets, q='to:{}'.format(user_name),
                                since_id=tweet_id, max_id=max_id, tweet_mode='extended').items()

    for reply in replies:
        if(reply.in_reply_to_status_id == tweet_id):
            urls.append(get_twitter_url(user_name, reply.id))
            try:
                for reply_to_reply in update_urls(reply, api, urls):
                    pass
            except Exception:
                pass
        max_id = reply.id
    return urls

def get_api():
    auth=tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api

def get_tweet(url):
    tweet_id = url.split('/')[-1]
    api = get_api()
    tweet = api.get_status(tweet_id)
    return tweet

def get_twitter_url(user_name, status_id):
    return "https://twitter.com/" + str(user_name) + "/status/" + str(status_id)


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1') 
    writer.save()
    processed_data = output.getvalue()
    return processed_data



with st.sidebar.form(key='my_form'):
    st.write("""
        ## Descargar tweets
        """)
    url = st.text_input('Ingresa la url por favor:')
    submit_button = st.form_submit_button(label='Procesar')

if url:
    api = get_api()
    tweet = get_tweet(url)
    urls = [url]
    urls = update_urls(tweet, api, urls)
    tweets = []
    for u in urls:
        tw = get_tweet(u)
        row = {}
        row['date'] = tw.created_at
        row['user'] = tw.user.screen_name
        row['text'] = tw.text
        tweets.append(row)

    df = pd.DataFrame(tweets)
    df["date"] = df["date"].dt.date

    df_xlsx = to_excel(df)
    st.write("# Resultados obtenidos")
    if len(df)>0:
        st.write(df)
        st.download_button(label='📥 Descargar Resultados',
                                        data=df_xlsx ,
                                        file_name= 'descarga_tweets.xlsx')
    else:
        st.write("Lo siento algo falló")