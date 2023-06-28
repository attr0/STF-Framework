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

from data import *

import subprocess
import logging
import signal
import time
import requests
import datetime
import os
import pandas as pd
import asyncio


from dataclasses import dataclass

@dataclass
class ModelConfig:
    ip: str = "127.0.0.1"
    port: int = 8080
    logdir: str = './'
    cluster_type: str = ''
    cluster_id: int = 0
    cluster_path: str = ''
    model_path: str = ''
    model_lib: str = ''
    dev_name: str = 'cpu'
    gpu_mem: int = 1024*1024*1024 # 1GB
    db_host: str = '127.0.0.1'
    db_port: int = 3306
    db_db: str = 'stf'
    db_user: str = 'stf'
    db_pwd: str = 'stf'

    def to_dict(self) -> dict:
        return self.__dict__

class Model:
    config: ModelConfig
    proc: subprocess.Popen = None
    logger: logging.Logger

    def __init__(self, logger: logging.Logger, config: ModelConfig) -> None:
        self.config = config
        self.logger = logger

    def init(self):
        if self.proc is not None:
            return
        # prepare flag
        self.logger.info(f"Starting Model of {self.config.cluster_type}_{self.config.cluster_id}")
        args = ["python", "model/run.py"]
        for k, v in self.config.to_dict().items():
            args.append(f"--{k}")
            args.append(str(v))
        # start process
        self.proc = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)

        # ping
        eflag = True
        for _ in range(3):
            try:
                url = f'http://{self.config.ip}:{self.config.port}/ping'
                requests.post(url, timeout=5)
                eflag = False
                if not eflag:
                    break
            except requests.exceptions.RequestException as e:
                continue
        if eflag:
            self.proc.terminate()
            self.proc = None
            raise Exception(f"Loading Failed on Model of {self.config.cluster_type}_{self.config.cluster_id}")

        self.logger.info(f"Loaded Model of {self.config.cluster_type}_{self.config.cluster_id}")

    async def predict(self, step: int, start_date: datetime.datetime, end_date: datetime.datetime) -> pd.DataFrame:
        payload = {
            'step': step,
            'start_date': start_date.isoformat(timespec='milliseconds'),
            'end_date': end_date.isoformat(timespec='milliseconds'),
        }
        eflag = True
        result = {}
        for _ in range(3):
            try:
                url = f'http://{self.config.ip}:{self.config.port}/predict'
                result = requests.post(url, json=payload, timeout=120).json()
                eflag = False
                if not eflag:
                    break
            except requests.exceptions.RequestException as e:
                continue
        if eflag:
            raise Exception(f"Prediction Timeout on Model of {self.config.cluster_type}_{self.config.cluster_id}")
        
        if result['code'] != 200:
            raise Exception(f"Prediction Error on Model of {self.config.cluster_type}_{self.config.cluster_id} with reason: {result['err']}")

        return from_str_to_pandas(result['msg'])
    
    def shutdown(self) -> None:
        if self.proc is not None:
            self.proc.terminate()
            self.proc = None
        self.logger.info(f"Shutdown Model of {self.config.cluster_type}_{self.config.cluster_id}")



if __name__ == "__main__":
    async def test():
        c_list = []
        for i in range(4):
            print(f"Good Morning from {i}\n\n")
            from dateutil import parser
            s = parser.parse("2022-05-01 00:00:00") 
            e = parser.parse("2022-05-01 00:12:00") 
            pred = asyncio.create_task(m.predict(10, s, e))
            c_list.append(pred)
        
        r_list = []
        for i, v in enumerate(c_list):
            await v
            r_list.append(v.result())
            print(f"Good night from {i}\n\n")
        return r_list
    
    logger = logging
    logger.basicConfig(level = logging.INFO)

    c = ModelConfig()
    c.logdir = "./test/logs"
    c.cluster_type = "FLOW"
    c.cluster_id = 2
    c.cluster_path = "./model/BaseModel.py"
    c.model_path = "./test/0.h5"
    c.model_lib = "./model/BaseModel.py"
    m = Model(logger, c)
    m.init()
    
    def signal_handler(*args):
        m.shutdown()
        print("Bye Bye~")
        os._exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGABRT, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    c = test()
    x = asyncio.run(c)
    print(x[3])

    while True:
        print("We are in the parallel unvierse")
        time.sleep(60*60*24*30)

