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
import datetime
import io
import pymysql
import os
import logging

"""
TODO: Wait for database system
"""
class DataFetcher:
    cluster_type: str
    cluster_id: int

    isLocalFile = False
    db_conn: pymysql.connect
    df: pd.DataFrame

    def init(self, logger: logging.Logger, cluster_type: str, cluster_id: int):
        self.cluster_type = cluster_type
        self.cluster_id = cluster_id

        if len(os.environ['H5_PATH']) != 0:
            # local file
            self.isLocalFile = True
            self.df = pd.read_hdf(os.environ['H5_PATH'], "df")
            logger.info(f"[Data Fetcher] Init on the local file: {os.environ['H5_PATH']}")
        else:
            raise Exception("[Data Fetcher] Database Model has not been implemented yet")

            # use database
            self.db_conn = pymysql.connect(
                    host=os.environ['DB_HOST'],
                    port=int(os.environ['DB_PORT']),
                    database=os.environ['DB_DB'],
                    user=os.environ['DB_USER'],
                    passwd=os.environ['DB_PWD'],
                    charset="utf8",
                )


    def fetch(self, start_date: datetime.datetime, end_date: datetime.datetime) -> pd.DataFrame:
        if self.isLocalFile:
            # local file
            t: pd.DataFrame = self.tmp_df.loc[start_date:end_date]
            return t
        else:
            # database
            raise Exception("[Data Fetcher] Database Model has not been implemented yet")


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


if __name__ == "__main__":
    d = DataFetcher()
    d.init("flow", 2)
    from dateutil import parser
    s = parser.parse("2022-05-01 00:00:00") 
    e = parser.parse("2022-05-01 00:12:00") 
    x = d.fetch(s, e)
    print(x)
