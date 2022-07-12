import snscrape.modules.twitter as sntwitter
import pandas as pd
import streamlit as st
from io import BytesIO

# busqueda de conversaciones en twitter by Francisco Carreño

# Metodo de busqueda
def search_by_ID(tweet_id):
    tweets_list = [] #lista con los tweets que luego sera convertida a df
    # Tweet padre:
    for i,tweet1 in enumerate(sntwitter.TwitterTweetScraper(tweetId=tweet_id,mode=sntwitter.TwitterTweetScraperMode.SINGLE).get_items()):
        tweets_list.append([tweet1.date, tweet1.id, tweet1.content, tweet1.user.username])
    # Resto de Tweets
    # me enferma escribir la palabra tweet
    filtro = f'conversation_id:{tweet_id} filter:safe'
    search = sntwitter.TwitterSearchScraper(filtro).get_items()
    total = len(list(search))
    my_bar = st.progress(0)
    for i,tweet in enumerate(sntwitter.TwitterSearchScraper(filtro).get_items()):
        tweets_list.append([tweet.date, tweet.id, tweet.content, tweet.user.username])
        my_bar.progress(int(i/total*100))
    my_bar.progress(100)
    return tweets_list
# metodo para guardar el archivo en excel y preparar para la descarga
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
    submit_button = st.form_submit_button(label='Procesar 👈')
    st.write("Creado por Francisco Carreño")

if url:
    tweet_id = url.split('/')[-1] #obtener el id del link
    tweets_list = search_by_ID(tweet_id) #buscar los los tweets
    df = pd.DataFrame(tweets_list, columns=['Datetime', 'Tweet Id', 'Text', 'Username']) #lo paso a df
    df["Datetime"] = df["Datetime"].dt.date # convierto las fechas
    df_xlsx = to_excel(df) # y lo guardo en excel
    n_tweets = len(df)

    st.write("# Resultados obtenidos 😎")
    if len(df)>0:
        st.write(f"se encontraron {n_tweets} tweets!")
        st.write("Al final encontrarás el botón para descargar los resultados")
        st.write(df)
        st.download_button(label='📥 Descargar Resultados',
                                        data=df_xlsx ,
                                        file_name= 'descarga_tweets.xlsx')
        
    else:
        st.write("Lo siento algo falló 😫")