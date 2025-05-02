import joblib
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


MODEL_PATH = 'trained_model/model.pkl'


def train_model(data: pd.DataFrame):
    X = data[['area', 'descricao', 'classificacao']]
    y = data['causa_raiz']

    # Pré-processamento: colunas categóricas e texto
    preprocessor = ColumnTransformer(transformers=[
        ('area', OneHotEncoder(handle_unknown='ignore'), ['area']),
        ('classificacao', OneHotEncoder(handle_unknown='ignore'), ['classificacao']),
        ('descricao', TfidfVectorizer(), 'descricao')
    ])

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    pipeline.fit(X, y)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)


def predict(data: pd.DataFrame):
    pipeline = joblib.load(MODEL_PATH)

    # remove colunas que não fazem parte do X original
    data = data.drop(columns=['causa_raiz', 'capa'], errors='ignore')

    return pipeline.predict(data)


def explain_prediction(data: pd.DataFrame, prediction: str) -> str:
    descricao = data.get('descricao', [''])[0]
    classificacao = data.get('classificacao', [''])[0]
    area = data.get('area', [''])[0]

    return f"""
Com base na descrição do desvio ocorrido em "{area}", onde foi relatado que "{descricao}", e considerando que o desvio foi classificado como "{classificacao}",
o sistema identificou padrões similares em casos anteriores e previu que a causa raiz mais provável seja:

👉 {prediction.upper()}.

Essa sugestão é feita com base em recorrência de padrões em desvios anteriores e pode ajudar na definição de ações corretivas adequadas.
"""
