import pandas as pd
import re
from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords

def preprocess_text(text):
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    return text

df = pd.read_csv("restaurants_reviews.csv")
df['ProcessedReviews'] = df['reviews'].apply(preprocess_text)

def extract_tags(text):
    tags = []
    tokens = word_tokenize(text)
    tagged_tokens = pos_tag(tokens)
    
    allowed_tags = ['NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS']
    for word, tag in tagged_tokens:
        if tag in allowed_tags and word not in stopwords.words('english'):
            tags.append(word)
    
    return tags

df['Tags'] = df['ProcessedReviews'].apply(extract_tags)
df['Tags'] = df['Tags'].apply(lambda tags: ', '.join(tags))

restaurant_tags = df[['restaurant_id', 'Tags']]
restaurant_tags.to_csv('restaurant_tags.csv', index=False)

print("restaurant_tags.csv has been created successfully.")