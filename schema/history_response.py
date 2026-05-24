
from schema.prediction_response import PredictionResponse
from pydantic import BaseModel
from schema.user_input import UserInput

class HistoryRecord(BaseModel):
    input: UserInput
    prediction: PredictionResponse