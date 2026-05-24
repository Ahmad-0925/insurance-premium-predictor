from fastapi import FastAPI, Header, HTTPException
from schema.user_input import UserInput,LoginInput,users
from config.city_tier import tier_1_cities,tier_2_cities
import pandas as pd
from model.predict import predict_output,MODEL_VERSION,model
import json
from fastapi.responses import JSONResponse
from record.history_data import HISTORY_FILE,history
from schema.prediction_response import PredictionResponse
from schema.history_response import HistoryRecord
app = FastAPI()




@app.get('/')
def home():
    return {'message':'Insurance Premium Predictor'}
 

#machine readable# So thats why for cloud deployment
@app.get('/health')
def health_check(): 
    return{
        'status':'OK',
        'version':MODEL_VERSION,
        'model_loaded':model is not None
    }

@app.post("/login")
def login(data: LoginInput):
    if data.username in users and users[data.username] == data.password:
        return {
            "message": "Login successful",
            "token": f"token_{data.username}_123"
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/secure-predict", response_model=PredictionResponse)
def secure_predict(data: UserInput):
    try:
        user_input = {
            'bmi': data.bmi,
            'age_group': data.age_group,
            'lifestyle_risk': data.lifestyle_risk,
            'city_tier': data.city_tier,
            'income_lpa': data.income_lpa,
            'occupation': data.occupation
        }
        return predict_output(user_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict-save",response_model=HistoryRecord)
def predict_save(data: UserInput):
    try:
        user_input = {
            'bmi': data.bmi,
            'age_group': data.age_group,
            'lifestyle_risk': data.lifestyle_risk,
            'city_tier': data.city_tier,
            'income_lpa': data.income_lpa,
            'occupation': data.occupation
        }
        prediction = predict_output(user_input)  

        record = {
            "input": data.model_dump(),
            "prediction": prediction  
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    history.append(record)

    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save history")

    return record


@app.get("/history")
def get_history():
    return history