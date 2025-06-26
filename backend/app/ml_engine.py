import joblib
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
from .models import Deviation
import eli5

MODEL_PATH = os.path.join('model', 'deviation_model.joblib')
VECTORIZER_PATH = os.path.join('model', 'vectorizer.joblib')

def get_model_and_vectorizer():
    if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
        return model, vectorizer
    return None, None

def predict_deviation(description):
    model, vectorizer = get_model_and_vectorizer()
    if model is None or vectorizer is None:
        raise FileNotFoundError("Modelo ou vetorizador não encontrado. Treine o modelo primeiro.")

    text_vectorized = vectorizer.transform([description])
    prediction = model.predict(text_vectorized)[0]
    probabilities = model.predict_proba(text_vectorized)
    
    # As classes são ordenadas, então a primeira prob é de 'improcedente' e a segunda de 'procedente'
    prob_improcedente = probabilities[0][0]
    prob_procedente = probabilities[0][1]

    return prediction, max(probabilities[0])

def train_model():
    deviations = Deviation.query.all()
    if len(deviations) < 10: # Mínimo de amostras para treinar
        return {"error": "Dados insuficientes para o treinamento. Mínimo de 10 registros necessários."}

    df = pd.DataFrame([d.to_dict() for d in deviations])
    df = df.dropna(subset=['deviation_description', 'final_decision'])

    if df.shape[0] < 10:
        return {"error": "Dados válidos insuficientes após limpeza."}
    
    # Mapear decisão para binário (0: Improcedente, 1: Procedente)
    df['target'] = df['final_decision'].apply(lambda x: 1 if 'procedente' in x.lower() else 0)

    X_train, X_test, y_train, y_test = train_test_split(
        df['deviation_description'], df['target'], test_size=0.2, random_state=42
    )

    pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer(stop_words=None, max_features=1000)),
        ('classifier', MultinomialNB())
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)

    os.makedirs('model', exist_ok=True)
    joblib.dump(pipeline.named_steps['classifier'], MODEL_PATH)
    joblib.dump(pipeline.named_steps['vectorizer'], VECTORIZER_PATH)

    return {
        "message": "Treinamento concluído com sucesso!",
        "accuracy": accuracy,
        "report": report
    }

def explain_prediction(description):
    model, vectorizer = get_model_and_vectorizer()
    if model is None or vectorizer is None:
        raise FileNotFoundError("Modelo ou vetorizador não encontrado.")

    # A função de explicação do eli5 funciona melhor com o classificador e o vetorizador separados
    explanation = eli5.format_as_text(eli5.explain_weights(model, vec=vectorizer, top=10))
    
    prediction_explanation = eli5.format_as_text(eli5.explain_prediction(
        model, 
        description, 
        vec=vectorizer
    ))

    return {
        "general_features": explanation,
        "prediction_specific_features": prediction_explanation
    }