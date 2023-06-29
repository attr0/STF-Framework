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


import tomli
import traceback
import os
import sys

from dataclasses import dataclass, field
from typing import List

@dataclass
class CoreConfig:
    dev: str = ''
    listen_ip: str = ''
    min_port: int = 0
    gpu_mem: int = 0

    def load_conf(self, conf: dict):        
        for k in self.__dict__.keys():
            self.__setattr__(k, conf[k])


@dataclass
class DataBaseConfig:
    host: str = ''
    port: int = 0
    db: str = ''
    user: str = ''
    pwd: str = ''

    def load_conf(self, conf: dict):        
        for k in self.__dict__.keys():
            self.__setattr__(k, conf[k])

@dataclass
class SystemConfig:
    name: str = ""
    cluster_path: str = ""
    cluster_number: int = 0
    logdir: str = './'
    model_lib: str = ''
    model_paths: List[str] = field(default_factory=list)

    def load_conf(self, conf: dict):        
        for k in self.__dict__.keys():
            self.__setattr__(k, conf[k])


core_config = CoreConfig()
database_config = DataBaseConfig()
system_config_list: List[SystemConfig] = []


def load_configuration():
    cmd_conf = {}
    
    with open(os.environ['conf'], 'rb') as f:
        cmd_conf = tomli.load(f)

    try:
        core_config.load_conf(cmd_conf['core'])
        database_config.load_conf(cmd_conf['database'])

        for v in cmd_conf['system'].values():
            s = SystemConfig()
            s.load_conf(v)
            if len(s.model_paths) != s.cluster_number:
                raise Exception(f"the number of model is not matched with the cluster. (model_paths_len={len(s.model_paths)} != cluster_num={s.cluster_number})")
            system_config_list.append(s)

    except Exception as e:
        print(f"Cannot Parse the configuration.", file=sys.stderr)
        traceback.print_exc(limit=1, file=sys.stdout)
        sys.exit(-1)

if __name__ == "__main__":
    os.environ['conf'] = './core.toml'
    load_configuration()