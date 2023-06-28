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
import random
import base64
import datetime
import io
import pymysql
import os

DB = pymysql.connect(
        host=os.environ['DB_HOST'],
        port=int(os.environ['DB_PORT']),
        database=os.environ['DB_DB'],
        user=os.environ['DB_USER'],
        passwd=os.environ['DB_PWD'],
        charset="utf8",
    )

def fetch_data(start_date: datetime.datetime, end_date: datetime.datetime) -> pd.DataFrame:
    pass


def from_str_to_pandas(data: str) -> pd.DataFrame:
    # from str to base64 bytes
    data = data.encode("ascii")
    # from base64 bytes to bytes
    data = base64.b64decode(data)
    # create buffer
    buffer = io.BytesIO(data)
    # load from buffer
    data = pd.read_pickle(buffer)
    # retrun result
    return data

def from_pandas_to_str(data: pd.DataFrame) -> str:
    buffer = io.BytesIO()

    # from pandas to bytes
    data.to_pickle(buffer)
    # from bytes to base64 bytes
    data = base64.b64encode(buffer.getvalue())
    # from base64 bytes to str
    return data.decode("ascii")


if __name__ == "__main__":
    input_data = []
    for i in range(12):
        v = []
        for i in range(326):
            v.append(random.random())
        input_data.append(v)
    input_data = pd.DataFrame(input_data)
    input_data = input_data.reindex([x for x in range(325, -1, -1)], axis=1)

    print(input_data, input_data.shape)
    print("<\t>\t" * 30)

    a = from_pandas_to_str(input_data)
    print(a)
    print("<\t>\t" * 30)

    b = from_str_to_pandas(a)
    print(b, b.shape)
    