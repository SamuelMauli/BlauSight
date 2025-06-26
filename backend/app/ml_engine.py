import joblib
import os
import pandas as pd
from flask import current_app
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

def train_model(data: pd.DataFrame):
    model_path = current_app.config['MODEL_PATH']
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    X = data['descricao']
    y = data['causa_raiz']

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('classifier', MultinomialNB())
    ])

    pipeline.fit(X, y)
    joblib.dump(pipeline, model_path)

def predict_from_text(description: str):
    model_path = current_app.config['MODEL_PATH']
    pipeline = joblib.load(model_path)
    
    prediction = pipeline.predict([description])
    
    return prediction[0]

def explain_prediction(description: str, prediction: str) -> str:
    return f"""
Com base na descrição do desvio fornecida: "{description}", o sistema identificou padrões nos dados históricos e previu que a causa raiz mais provável é:

👉 {prediction.upper()}
"""