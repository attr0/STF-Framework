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

from model import *
from model_factory import *

import pandas as pd
import logging
import asyncio

from typing import List

class System:
    logger: logging.Logger
    config: SystemConfig
    model_list: List[Model] = []
    model_conf_list: List[ModelLaunchConfig] = []
    
    def __init__(self, logger: logging.Logger, config: SystemConfig) -> None:
        self.logger = logger
        self.config = config

    def gen_model_config(self, i: int, model_path: str):
        m = ModelLaunchConfig()
        m.logdir = self.config.logdir
        m.cluster_type = self.config.name
        m.cluster_id = i + 1
        m.cluster_path = self.config.cluster_path
        m.model_lib = self.config.model_lib
        m.model_path = model_path
        m.h5_path = self.config.h5_path
        return m

    def init(self) -> None:
        self.logger.info(f"[System-{self.config.name}] Starting")

        if len(self.model_list) != 0:
            raise Exception(f"[System-{self.config.name}] Init Multiple times!")
        
        for i, model_path in enumerate(self.config.model_paths):
            # fill data
            m_conf = self.gen_model_config(i, model_path)
            self.model_conf_list.append(m_conf)
            
            # gen
            m = mf.generate(self.logger, m_conf)
            m.init()
            self.model_list.append(m)

        self.logger.info(f"[System-{self.config.name}] Successfully Loaded")
        
    def shutdown(self):
        for m in self.model_list:
            m.shutdown()
        self.logger.info(f"[System-{self.config.name}] Shutdown")


    async def predict(self, selection: List[str], step: int, start_date: datetime.datetime, 
                      end_date: datetime.datetime) -> pd.DataFrame:
        
        c_list: List[asyncio.Task] = []
        p_list: List[pd.DataFrame] = []

        for m in self.model_list:
            c_list.append(asyncio.create_task(m.predict(step, start_date, end_date)))

        for c in c_list:
            try:
                await c
                p_list.append(c.result())
            # reraise the exception explicitly
            except Exception as e:
                raise e
            
        df = pd.concat(p_list, axis=1)
        if len(selection) != 0:
            df = df.reindex(columns=selection)

        return df