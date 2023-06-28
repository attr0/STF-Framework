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

import numpy as np
import random
import base64
import io

def from_str_to_numpy(data: str) -> np.ndarray:
    # from str to base64 bytes
    data = data.encode("ascii")
    # from base64 bytes to bytes
    data = base64.b64decode(data)
    # create buffer
    buffer = io.BytesIO(data)
    # load from buffer
    data = np.load(buffer, allow_pickle=True)
    # retrun result
    return data

def from_numpy_to_str(data: np.ndarray) -> str:
    # from numpy to bytes
    data = data.dumps()
    # from bytes to base64 bytes
    data = base64.b64encode(data)
    # from base64 bytes to str
    return data.decode("ascii")


if __name__ == "__main__":
    input_data = []
    for i in range(12):
        v = []
        for i in range(326):
            v.append(random.random())
        input_data.append(v)
    input_data = np.array([input_data])

    # print(input_data, input_data.shape)
    # print("<\t>\t" * 30)

    # a = from_numpy_to_str(input_data)
    # print(a)
    # print("<\t>\t" * 30)

    # s = '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'
    # b = from_str_to_numpy(s)
    # print(b, b.shape)
    