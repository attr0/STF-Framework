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

from BaseModel import *

import tensorflow as tf
import keras
import numpy as np
import random
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
    name: str
    model: keras.Model
    input_shape: tuple
    model_wapper: BaseModel

    def init(self, name: str, dev_name: str, gpu_mem: int, model_path: int, model_lib: str) -> None:
        self.name = name

        # init gpu
        tf.get_logger().setLevel('ERROR')
        if dev_name != "cpu":
            gpus = tf.config.list_physical_devices("GPU")
            if dev_name not in gpus:
                raise Exception(f"No gpu named: {dev_name}")

            # Restrict TensorFlow to only allocate {gpu_mem_size}Bytes of memory on the {gpu_dev}
            try:
                tf.config.set_logical_device_configuration(
                    dev_name,
                    [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=gpu_mem) ],
                    )
            except RuntimeError as e:
                # Virtual devices must be set before GPUs have been initialized
                raise Exception(e)
        
        # load model
        self.model = keras.models.load_model(model_path, compile=False)
        self.model.compile(optimizer="SGD", loss=None, metrics=None)
        # save input shape
        self.input_shape = list(self.model.layers[0].input_shape[0])

        # create wapper
        wapper_class = load_model_class_from_path(model_lib)
        self.model_wapper = wapper_class(self.name, self.model)

    """
    Note, x_input must have an additional dimension for batch operation.
    Eg., the input is 36x128, then x_input should be 1x36x128
    """
    def predict(self, step: int, x_input: np.ndarray):
        for i in range(1, len(self.input_shape)):
            if x_input.shape[i] != self.input_shape[i]:
                raise Exception(f"Input shape is incorrect. Expect: {self.input_shape}")
        
        # call remote
        res = self.model_wapper.predict(step, x_input)

        return res


if __name__ == "__main__":
    m = Model()
    m.init("flow_4", "cpu", 0, "./test/0.h5", './BaseModel.py')
    print(f"input_shape: {m.input_shape}")
    
    input_data = []
    for i in range(12):
        v = []
        for i in range(326):
            v.append(random.random())
        input_data.append(v)
    input_data = np.array([input_data])

    output_data = m.predict(input_data)
    print(output_data)