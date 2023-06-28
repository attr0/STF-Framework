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

import keras
import pandas as pd
import logging

from abc import ABC
from abc import abstractmethod

"""
The model calling warpper class
"""
class BaseModel(ABC):
    logger: logging.Logger   # the log instance
    model: keras.Model       # the actual keras model

    cluster_type: str        # cluster type. FLOW, SPEED
    cluster_id: int          # cluster id
    cluster_path: str        # the cluster file path

    """
    Resource Init

    Note:
        - You may init the cluster here
    """    
    def __init__(self, logger: logging.Logger, model: keras.Model, cluster_type: str, 
                 cluster_id: int, cluster_path: str) -> None:
        super().__init__()
        self.logger = logger
        self.model = model
        self.cluster_type = cluster_type
        self.cluster_id = cluster_id
        self.cluster_path = cluster_path

    """
    Make contiously prediction of {step} step from the {X_input}

    Note:
        - The clustering should be enforced here
        - Data preprocess and postprocess should be done here
        - Raise exception as soon as possible. Must not make tensorflow crash! (e.g. input size check)
        - The returned pd.DataFrame must have correct indexes and column names.
    """
    @abstractmethod
    def predict(self, step: int, X_input: pd.DataFrame) -> pd.DataFrame:
        pass

"""
This is an example of BaseModel's derived class

Requirement:
    - The class name must be called 'PredictionModel'

"""
class PredictionModel(BaseModel):
    def __init__(self, logger: logging.Logger, model: keras.Model, cluster_type: str, 
                 cluster_id: int, cluster_path: str) -> None:
        super().__init__(logger, model, cluster_type, cluster_id, cluster_path)
        self.logger.info("Hello World from Prediction Model")

    def predict(self, step: int, X_input: pd.DataFrame) -> pd.DataFrame:
        self.logger.info("Working Noise from Prediction Model")

        return X_input