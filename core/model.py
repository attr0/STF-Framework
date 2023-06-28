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
class ModelLaunchConfig:
    # filled by model factory
    ip: str = "127.0.0.1"
    port: int = 8080
    dev_name: str = 'cpu'
    gpu_mem: int = 1024*1024*1024 # 1GB
    
    # filled by system
    logdir: str = './'
    cluster_type: str = ''
    cluster_id: int = 0
    cluster_path: str = ''

    # filled by config
    model_path: str = ''
    model_lib: str = ''

    # filled by system
    db_host: str = '127.0.0.1'
    db_port: int = 3306
    db_db: str = 'stf'
    db_user: str = 'stf'
    db_pwd: str = 'stf'

    def to_dict(self) -> dict:
        return self.__dict__

class Model:
    config: ModelLaunchConfig
    proc: subprocess.Popen = None
    logger: logging.Logger

    def __init__(self, logger: logging.Logger, config: ModelLaunchConfig) -> None:
        self.config = config
        self.logger = logger

    def init(self):
        if self.proc is not None:
            return
        # prepare flag
        self.logger.info(f"[Model-{self.config.cluster_type}_{self.config.cluster_id}] Loading")
        args = ["python", "model_instance/run.py"]
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
            raise Exception(f"[Model-{self.config.cluster_type}_{self.config.cluster_id}] Loading Failure. (Reason: Timeout)")

        self.logger.info(f"[Model-{self.config.cluster_type}_{self.config.cluster_id}] Load Successfully")

    async def predict(self, step: int, start_date: datetime.datetime, end_date: datetime.datetime) -> pd.DataFrame:
        payload = {
            'step': step,
            'start_date': start_date.isoformat(timespec='milliseconds'),
            'end_date': end_date.isoformat(timespec='milliseconds'),
        }
        eflag = True
        result = {}
        self.logger.debug(f"[Model-{self.config.cluster_type}_{self.config.cluster_id}] Predicts {start_date}->{end_date}, step={step}")
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
            raise Exception(f"[Model-{self.config.cluster_type}_{self.config.cluster_id}] Prediction Failed. (Reason: Timeout)")
        
        if result['code'] != 200:
            raise Exception(f"[Model-{self.config.cluster_type}_{self.config.cluster_id}] Prediction Failed. (Reason: {result['err']})")

        return from_str_to_pandas(result['msg'])
    
    def shutdown(self) -> None:
        if self.proc is not None:
            self.proc.terminate()
            self.proc = None
        self.logger.info(f"[Model-{self.config.cluster_type}_{self.config.cluster_id}] Shutdown")