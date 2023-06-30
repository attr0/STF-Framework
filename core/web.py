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
from model_factory import *
from system import *

from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import Dict, List
import json

import logging
import datetime
import signal

#================================
# Global Resources
#===============================

app = FastAPI(
        title="STF Core Backend Model",
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

logger = logging.getLogger("uvicorn.error")
system_mapping: Dict[str, System] = {}

@app.on_event("startup")
def startup():
    # handle win32 signal
    try:
        # for windows
        import win32api
        def console_shutdown(x):
            shutdown()
            os.kill(os.getpid(), signal.SIGINT)
    
        win32api.SetConsoleCtrlHandler(console_shutdown)
        logger.info("Win32 Signal Hanlder Registered")
    except:
        pass

    # banner
    print(banner)

    try:
        # resolve and start
        load_configuration()
        mf.init(core_config.listen_ip, core_config.dev, core_config.min_port)
        for sc in system_config_list:
            system_mapping[sc.name] = System(logger, sc)
            system_mapping[sc.name].init()
    except Exception as e:
        # shutdown resources
        shutdown()
        raise(e)

@app.on_event("shutdown") # never worked
def shutdown():
    for _, v in system_mapping.items():
        v.shutdown()
    logger.info("See you next time~")

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
        msg="",
        err=""
    )

# #================================
# # Terminate
# #===============================
# @app.post("/shutdown")
# async def shutdown_handler() -> None:
#     shutdown()
#     os.kill(os.getpid(), signal.SIGINT)


# =============================
# Prediction
# =============================
class PredictionReq(BaseModel):
    system: str
    step: int
    start_date: datetime.datetime
    end_date: datetime.datetime
    selection: List[str]

class PredictionRsp(BaseModel):
    code: int = 200,
    msg: Dict[str, List[float]]
    err: str = ""

@app.post('/predict')
async def predict_handler(req: PredictionReq) -> PredictionRsp:
    try:
        if req.system not in system_mapping.keys():
            raise Exception(f"Prediction Error. System-{req.system} does not exist")
        
        s = system_mapping[req.system]
        pred = await s.predict(req.selection, req.step, req.start_date, req.end_date)
        pred = from_pandas_to_dict(pred)
        r = PredictionRsp(code=200, msg=pred, err="")
        r = json.dumps(r.__dict__, allow_nan=True)
        return Response(content=r, media_type='application/json')
    
    except Exception as e:
        logger.error(f"[System-{req.system}] Prediction Error: {e}", stack_info=True, stacklevel=1)
        return PredictionRsp(
            code=300,
            msg="",
            err=str(e),
        )