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

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from base_model import *

import tensorflow as tf
import keras
import pandas as pd
import logging
import sys
import importlib

from pathlib import Path

def load_model_class_from_path(path: str) -> BaseModel:
    if not path.endswith('.py'):
        raise Exception("Not a .py file")
    
    # load
    P = Path(path)
    sys.path.insert(0, str(P.parent))
    module = importlib.import_module(str(P.name)[:-3])
    importlib.reload(module)
    sys.path.pop(0)

    return module.PredictionModel

class Model:
    logger: logging.Logger
    model: keras.Model
    model_wapper: BaseModel

    def init(self, logger: logging.Logger, dev_name: str, gpu_mem: int, 
             model_path: int, model_lib: str, cluster_type: str, cluster_id: int, 
             cluster_path: str) -> None:
        self.logger = logger

        # init gpu
        tf.get_logger().setLevel('ERROR')
        if dev_name == "cpu":
            self.logger.info(f"[Model] Running on cpu")
        else: # GPU
            gpus = tf.config.list_physical_devices("GPU")
            # Restrict TensorFlow to only allocate {gpu_mem_size}Bytes of memory on the {gpu_dev}
            try:
                tf.config.set_logical_device_configuration(
                    gpus[0],
                    [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=gpu_mem) ],
                    )
            except RuntimeError as e:
                # Virtual devices must be set before GPUs have been initialized
                raise Exception(e)
            gpus = tf.config.list_logical_devices('GPU')
            self.logger.info(f"[Model] Running on {gpus[0]}")
        
        # load model
        self.model = keras.models.load_model(model_path, compile=False)
        self.model.compile(optimizer="SGD", loss=None, metrics=None)

        # create wapper
        wapper_class = load_model_class_from_path(model_lib)
        self.model_wapper = wapper_class(logger, self.model, cluster_type, cluster_id, cluster_path)
        self.logger.info(f"[Model] Load Successfully")


    def predict(self, step: int, x_input: pd.DataFrame):
        # call lib
        res = self.model_wapper.predict(step, x_input)

        return res