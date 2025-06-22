import pandas as pd
import numpy as np
import pickle

# Load models and data
tf_idf_vectorizer = pickle.load(open("models/tf_idf_vectorizer.pkl", "rb"))
sentiment_model = pickle.load(open("models/sentiment_model.pkl", "rb"))
similarity_matrix = pickle.load(open("models/similarity_matrix.pkl", "rb"))
review_df = pd.read_csv("data/review_df.csv")

def clean_text(text):
    return text.lower()

def recommend_products(user_id, top_n=20, final_n=5):
    user_item_matrix = pd.pivot_table(review_df, index='user_id', columns='name', values='reviews_rating')
    if user_id not in user_item_matrix.index:
        return []

    user_ratings = user_item_matrix.loc[user_id].dropna()
    scores = pd.Series(dtype=float)

    for item, rating in user_ratings.items():
        if item in similarity_matrix:
            similar_items = similarity_matrix[item]
            scores = scores.add(similar_items * rating, fill_value=0)

    scores = scores.drop(user_ratings.index, errors='ignore')
    top_20 = scores.sort_values(ascending=False).head(top_n).reset_index()
    top_20.columns = ['product', 'score']

    filtered_reviews = review_df[review_df['name'].isin(top_20['product'])].copy()
    filtered_reviews['cleaned_text'] = filtered_reviews['reviews_text'].apply(clean_text)
    
    try:
        X = tf_idf_vectorizer.transform(filtered_reviews['cleaned_text'])
    except ValueError:
        return []

    filtered_reviews['positive_score'] = sentiment_model.predict_proba(X)[:, 1]
    sentiment_scores = filtered_reviews.groupby('name')['positive_score'].mean().reset_index()

    final = pd.merge(top_20, sentiment_scores, left_on='product', right_on='name').drop(columns=['name'])
    final['hybrid_score'] = 0.6 * final['score'] + 0.4 * final['positive_score']
    
    return final.sort_values(by='hybrid_score', ascending=False).head(final_n).to_dict(orient='records')
