"""
 Copyright 2023 Haolin Zhang <me@hlz.ink>

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 """

from config import *
from model import *
from data import *

from fastapi import FastAPI
from pydantic import BaseModel

import logging
import asyncio
import os

#================================
# Global Resources
#===============================

app = FastAPI(
        title="STF Backend Prediction Model",
        version="0.0.1",
        contact={
            "name": "Haolin Zhang",
            "email": "me@hlz.ink",
        },
        license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
        redoc_url=None
    )

model_lock = asyncio.Lock()
logger = logging.getLogger("uvicorn.error")
model = Model()

#================================
# Setup
#================================

banner = """
 ______      _       _     _              ______ _______ _______ 
(_____ \    | |     (_)   (_)            / _____|_______|_______)
 _____) )__ | |_   _ _     _    _____   ( (____     _    _____   
|  ____/ _ \| | | | | |   | |  (_____)   \____ \   | |  |  ___)  
| |   | |_| | | |_| | |___| |            _____) )  | |  | |      
|_|    \___/ \_)__  |\_____/            (______/   |_|  |_|      
              (____/                                             
"""

@app.on_event("startup")
def startup():
    # banner
    print(banner)
    model.init(
        name=os.environ["model_name"],
        dev_name=os.environ["dev_name"],
        gpu_mem=int(os.environ["gpu_mem"]),
        model_path=os.environ["model_path"],
        model_lib=os.environ["model_lib"],
        )

@app.on_event("shutdown")
def shutdown():
    pass

#================================
# Echo
#===============================
class PingRsp(BaseModel):
    code: int = 200
    msg: str
    err: str = ""

@app.post("/ping")
async def ping_handler() -> PingRsp:
    return PingRsp(
        code=200,
        msg='busy' if model_lock.locked() else 'idle',
        err=""
    )

# =============================
# Prediction
# =============================
class PredictionReq(BaseModel):
    step: int
    data: str

class PredictionRsp(BaseModel):
    code: int = 200,
    msg: str
    err: str = ""

@app.post('/predict')
async def predict_handler(req_list: PredictionReq) -> PredictionRsp:
    async with model_lock:
        try:
            x_input = from_str_to_numpy(req_list.data)
            result = model.predict(req_list.step, x_input) 
            pred = from_numpy_to_str(result)

            return PredictionRsp(
                code=200,
                msg=pred,
                err="",
            )
        except Exception as e:
            return PredictionRsp(
                code=300,
                msg="",
                err=str(e),
            )