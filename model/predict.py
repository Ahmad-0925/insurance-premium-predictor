import pickle
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, 'modell.pkl'), 'rb') as f:
    model = pickle.load(f)

MODEL_VERSION = '1.0.0'

class_labels = model.classes_.tolist()  

def predict_output(user_input: dict):
    df = pd.DataFrame(user_input, index=[0])
    predicted_class = model.predict(df)[0]

    prob = model.predict_proba(df)[0]
    confidence = max(prob) 
    class_probs = dict(zip(class_labels, map(lambda p: round(p, 4), prob)))

    return {
        'predicted_category': predicted_class,
        'confidence': round(confidence, 4),
        'class_probabilities': class_probs
    }