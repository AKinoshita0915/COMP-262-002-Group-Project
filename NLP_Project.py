#!/usr/bin/env python
# coding: utf-8

# ### Data Exploration

# In[1]:


import pandas as pd
import gzip
import json

def parse(path):
  g = gzip.open(path, 'rb')
  for l in g:
    yield json.loads(l)

def getDF(path):
  i = 0
  df = {}
  for d in parse(path):
    df[i] = d
    i += 1
  return pd.DataFrame.from_dict(df, orient='index')

df = getDF("./Office_Products_5.json.gz")


# In[2]:


df


# This Dataset is an updated version of the Amazon review dataset released in 2014. As in the previous version, this dataset includes reviews (ratings, text, helpfulness votes), product metadata (descriptions, category information, price, brand, and image features), and links (also viewed/also bought graphs). In addition, this version provides the following features:
# 
# More reviews:
# The total number of reviews is 233.1 million (142.8 million in 2014).
# Newer reviews:
# Current data includes reviews in the range May 1996 - Oct 2018.
# Metadata:
# We have added transaction metadata for each review shown on the review page. Such information includes:
# Product information, e.g. color (white or black), size (large or small), package type (hardcover or electronics), etc.
# Product images that are taken after the user received the product.
# Added more detailed metadata of the product landing page. Such detailed information includes:
# Bullet-point descriptions under product title.
# Technical details table (attribute-value pairs).
# Similar products table.
# More categories:
# Includes 5 new product categories.
# 
# Source: https://nijianmo.github.io/amazon/index.html#code

# In[3]:


df.shape


# In[4]:


df.columns


# In[5]:


counts_of_reviews_per_product = df.groupby('asin').size()
for product, count_of_reviews_per_product in counts_of_reviews_per_product.iteritems():
  print(f'{product} has {count_of_reviews_per_product} reviews')
# counts_of_reviews_per_product


# In[6]:


len(counts_of_reviews_per_product)


# In[7]:


import matplotlib.pyplot as plt
import numpy as np

# Plot the distribution using matplotlib.pyplot.hist() function.
plt.hist(counts_of_reviews_per_product[:50], bins=np.arange(0, 100, 5))
plt.xlabel('Number of Reviews')
plt.ylabel('Frequency')
plt.title('Distribution of the Number of Reviews Across Products')
plt.show()


# In[8]:


counts_of_reviews_per_product[:10]


# In[9]:


plt.figure(figsize=(25,8))
plt.plot(counts_of_reviews_per_product[:10])
plt.xlabel('Product')
plt.ylabel('Number of reviews')
plt.title('Distribution of the number of reviews per product')
plt.show()


# In[10]:


counts_of_reviews_across_products = df.groupby(['asin', 'overall']).size()
# for product, count_of_reviews_per_product in counts_of_reviews_per_product.iteritems():
#   print(f'{product} has {count_of_reviews_per_product} reviews')
counts_of_reviews_across_products[:10]


# In[11]:


# Unstack the data to create a pivot table with product ids as rows and review ratings as columns
reviews_by_product_and_rating = counts_of_reviews_across_products[:10].unstack()

# Plot the distribution of the number of reviews per product per star rating as a histogram
reviews_by_product_and_rating.plot(kind='bar', stacked=True)
plt.xlabel('Product ID')
plt.ylabel('Number of reviews')
plt.title('Distribution of the number of reviews per product per star rating')
plt.show()


# In[12]:


counts_of_reviews_per_user = df.groupby('reviewerID').size()
for user, count_of_review in counts_of_reviews_per_user.iteritems():
  print(f'{user} has {count_of_review} reviews')


# In[13]:


plt.figure(figsize=(25,8))
plt.plot(counts_of_reviews_per_user[:10])
plt.xlabel('User')
plt.ylabel('Number of reviews')
plt.title('Distribution of the number of reviews per user')
plt.show()


# In[14]:


positive = df[df['overall'] > 3]
negative = df[df['overall'] < 3]
positive = positive.dropna()
negative = negative.dropna()


# In[16]:


# common words in positive review comments
import nltk
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
get_ipython().system('pip install wordcloud')
from wordcloud import WordCloud

stopwords = set(stopwords.words('english'))
stopwords.update(["br", "stuff", "href","taste", "product", "flavour","like", "coffee", "dog","flavor","buy"]) 

pos = " ".join(review for review in positive.reviewText)
wordcloud = WordCloud(stopwords=stopwords).generate(pos)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()


# In[17]:


# common words in negative review comments
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud
stopwords = set(stopwords.words('english'))
negreviews = " ".join(review for review in negative.reviewText)
wordcloud = WordCloud(stopwords=stopwords).generate(negreviews)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()


# In[18]:


df['reviewText']


# ### Pre-processing

# In[19]:


import random
n_samples = random.randint(500, 1000)
df_random = df.sample(n=n_samples)


# In[20]:


df_random.shape


# In[21]:


df_random


# In[22]:


def condition(overall):
  # print(df)
  rating = overall
  if rating in (4.0, 5.0):
    return 'Positive'
  elif rating == 3.0:
    return 'Neutral'
  elif rating in (1.0, 2.0):
    return 'Negative'

df_random['label'] = df_random['overall'].apply(condition)


# In[23]:


df_random


# In[24]:


final_df = pd.DataFrame(df_random['reviewText']) 


# In[25]:


type(final_df)


# In[26]:


final_df


# In[27]:


import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import string

nltk.download('stopwords')
nltk.download('punkt')

for _, review in final_df.iterrows():
  sentence = review['reviewText'].lower()
  sentence = sentence.translate(str.maketrans("", "", string.punctuation))

  # Tokenize the sentence into words and remove stop words
  stop_words = set(stopwords.words('english'))
  # Tokenize the sentence into words
  words = [word for word in nltk.word_tokenize(sentence) if word.lower() not in stop_words]

  if words:
    # Create the TF-IDF vectorizer object
    tfidf = TfidfVectorizer()

    # Fit and transform the words using the vectorizer object
    tfidf_matrix = tfidf.fit_transform(words)

    # Print the TF-IDF matrix
    print(tfidf_matrix.toarray())


# ### Modeling

# #### VADR

# In[28]:


get_ipython().system('pip install vaderSentiment')
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# In[29]:


# Valence Aware Dictionary and Sentiment Reasoner (VADR)
VADR_analyzer = SentimentIntensityAnalyzer()

predicted_sentiments = []
# Pass the analyzer for head 5 rows
for index, row in df_random.head().iterrows():
    vs = VADR_analyzer.polarity_scores(row["reviewText"])
    print(
        f"Index: {index}\n"+
        f"Sentimental Analysis Result: {vs}\n"+
        f"Overall rating category: {row.label}\n"+
        f"Full Text:\n{row.reviewText}\n"+
        "-"*50)
    if vs['neg'] > vs['pos']:
      sentiment = 'Negative'
    elif vs['pos'] > vs['neg']:
      sentiment= 'Positive'
    else:
      sentiment = 'Neutral'
    predicted_sentiments.append(sentiment)


# #### TextBlob

# In[32]:


get_ipython().system('pip install textblob')
from textblob import TextBlob


# In[33]:


list(final_df['reviewText'])


# ### Validation

# In[34]:


# VADR
predicted_sentiments = []
for index, row in df_random.iterrows():
    # Pass analyzer
    vs = VADR_analyzer.polarity_scores(row["reviewText"])
    if vs['neg'] > vs['pos']:
      sentiment = 'Negative'
    elif vs['pos'] > vs['neg']:
      sentiment= 'Positive'
    else:
      sentiment = 'Neutral'
    predicted_sentiments.append(sentiment)

(predicted_sentiments == df_random['label']).value_counts()


# In[35]:


# TextBlob
predicted_sentiments = []
for text in list(final_df['reviewText']):
  if isinstance(text, str):
    wiki = TextBlob(text)
    predicted_sentiments.append(wiki.sentiment)


# In[36]:


predicted_ratings = []
for predicted_sentiment in predicted_sentiments:
  if predicted_sentiment.polarity == 0:
    predicted_ratings.append('Neutral')
  elif predicted_sentiment.polarity < 0 :
    predicted_ratings.append('Negative')
  elif predicted_sentiment.polarity > 0 :
    predicted_ratings.append('Positive')


# In[37]:


(predicted_ratings == df_random['label']).value_counts()


# In[ ]:




