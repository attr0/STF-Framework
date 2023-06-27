from model import *

from fastapi import FastAPI
from typing import List
from pydantic import BaseModel

import asyncio

#================================
# Global Resources
#===============================

app = FastAPI()
model_lock = asyncio.Lock()

#================================
# Echo
#===============================
@app.post("/ping")
async def ping_handler():
    return {
        "code": 200,
        "msg": {'busy' if model_lock.locked else 'idle'}
        }

# =============================
# Prediction
# =============================
class PredictionReq(BaseModel):
    detector_history: List[List[float]]

@app.post('/predict')
async def predict_handler(req_list: PredictionReq):
    async with model_lock:
        try:
            raise Exception("test err")
        except Exception as e:
            return {
                "code": 300,
                "msg": str(e)
            }