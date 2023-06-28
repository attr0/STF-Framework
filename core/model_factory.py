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
from config import *

import logging
import asyncio
import os
import tensorflow as tf

from dataclasses import dataclass
from typing import List

@dataclass
class GPUInstance:
    gpu_id: int
    gpu_name: str
    gpu_mem: int  # Bytes


class ModelFactory:
    dev: str
    ip: str
    min_port: int
    next_port: int
    lock = asyncio.Lock()
    dev_list = List[GPUInstance]

    def __init__(self, ip:str, dev: str, min_port: int) -> None:
        self.dev = dev
        self.ip = ip
        self.min_port = min_port
        self.next_port = min_port
        
        if dev == 'gpu':
            devs = tf.config.list_physical_devices('GPU')
            for i, v in enumerate(devs):
                desc = os.popen(f'nvidia-smi.exe --query-gpu=memory.free -i 0 --format=csv').readlines()
                if len(desc) != 2:
                    break
                mem = int(desc[1].split(' ')[0]) * 1024 * 1024
                g = GPUInstance(i, v, mem)
                self.dev_list.append(g)
        elif dev == 'cpu':
            pass
        else:
            raise Exception(f"Not supported device: {dev}")

    def generate(self, logger: logging.Logger, config: ModelLaunchConfig) -> Model:
        self.lock.acquire()
        try:
            # computing instance
            if self.dev == 'cpu':
                config.dev_name = 'cpu'
            elif self.dev == 'gpu':
                # try find one
                g: GPUInstance = None
                for gi in self.dev_list:
                    if gi.gpu_mem > core_config.gpu_mem:
                        # enough memory
                        g = gi
                        gi.gpu_mem -= core_config.gpu_mem
                        break
                config.dev_name = g.gpu_name
                config.gpu_mem = core_config.gpu_mem

            # inject core config
            config.ip = self.ip
            config.port = self.min_port
            self.min_port += 1

            # inject db config
            config.db_host = core_config.db_host
            config.db_port = core_config.db_port
            config.db_db = core_config.db_db
            config.db_user = core_config.db_user
            config.db_pwd = core_config.db_pwd

            # init
            m = Model(logger, config)
            m.init()
            return m
        
        finally:
            self.lock.release()


mf = ModelFactory(
    ip=core_config.listen_ip,
    dev=core_config.dev,
    min_port=core_config.min_port,
)