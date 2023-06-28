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

import pandas as pd
import base64
import io

def from_str_to_pandas(data: str) -> pd.DataFrame:
    # from str to base64 bytes
    data = data.encode("ascii")
    # from base64 bytes to bytes
    data = base64.b85decode(data)
    # create buffer
    buffer = io.BytesIO(data)
    # load from buffer
    data = pd.read_pickle(buffer, compression='xz')
    # retrun result
    return data

def from_pandas_to_str(data: pd.DataFrame) -> str:
    buffer = io.BytesIO()

    # from pandas to bytes
    data.to_pickle(buffer, compression='xz')
    # from bytes to base64 bytes
    data = base64.b85encode(buffer.getvalue())
    # from base64 bytes to str
    return data.decode("ascii")

def from_pandas_to_dict(data: pd.DataFrame) -> dict:
    res = {}
    for k in data.columns:
        v = list(data.loc[:, k])
        res[k] = v
    return res