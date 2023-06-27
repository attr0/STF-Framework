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

import tensorflow as tf
import keras
import numpy as np
import random

from abc import ABC
from abc import abstractmethod

"""
The model calling warpper class
"""
class BaseModel(ABC):
    name: str                # the model name. Eg. FLOW_5, SPEED_11
    model: keras.Model       # the actual keras model

    def __init__(self, name: str, model: keras.Model) -> None:
        super().__init__()
        self.name = name
        self.model = model

    """
    Make contiously prediction of {step} step from the {X_input}

    Data preprocess and postprocess should be done here!
    """
    @abstractmethod
    def predict(self, step: int, X_input: np.ndarray):
        pass

"""
This is an example of BaseModel's derived class

Requirement:
    - The class name must be called 'PredictionModel'

"""
class PredictionModel(BaseModel):
    def __init__(self, name, model) -> None:
        super().__init__(name, model)
        print("Hello World from Prediction Model")

    def predict(self, step: int, X_input: np.ndarray):
        print("Working Noise from Prediction Model")

        return self.model.predict(X_input)