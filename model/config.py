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

import argparse
import os
import pathlib


cmdArgs: argparse.Namespace

cmdParser = argparse.ArgumentParser(prog='STF Model Instance',)

"""
For web
"""
cmdParser.add_argument('--ip', help="listened ip", default="0.0.0.0")
cmdParser.add_argument('--port', type=int, help="listened port", default="8080")
cmdParser.add_argument('--logdir', type=pathlib.Path, help="the log file directory", default='./')

"""
For model
"""
cmdParser.add_argument('--cluster_type', help="cluster type", required=True)
cmdParser.add_argument('--cluster_id', type=int, help="cluster id", required=True)
cmdParser.add_argument('--cluster_path', type=argparse.FileType('r'), help="the path to prediction model", required=True)

cmdParser.add_argument('--model_path', type=argparse.FileType('r'), help="the path to prediction model", required=True)
cmdParser.add_argument('--model_lib', type=argparse.FileType('r'), help="the path to prediction model lib script", required=True)
cmdParser.add_argument('--dev_name', help="which device should this model runs on. ('cpu' or a physical gpu device name)", required=True)
cmdParser.add_argument('--gpu_mem', type=int, help="the limit for gpu memory. (not work when use 'cpu' in dev_name)", default=0)

"""
For database
"""
# cmdParser.add_argument('--db_host', default="127.0.0.1")
# cmdParser.add_argument('--db_port', default="3306")
# cmdParser.add_argument('--db_db', default="stf")
# cmdParser.add_argument('--db_user', default="stf")
# cmdParser.add_argument('--db_pwd', default="stf")

# for local test only
cmdParser.add_argument('--db_host',  help="database host", default="36.133.145.76")
cmdParser.add_argument('--db_port', help="database port", type=int, default=53306)
cmdParser.add_argument('--db_db', help="database name", default="acloud")
cmdParser.add_argument('--db_user', help="database user", default="acloud")
cmdParser.add_argument('--db_pwd', help="database password", default="acloud")


def arg_to_env(args: argparse.Namespace):
    for i in args._get_kwargs():
        t = tuple(i)
        if type(t[1]) == str:
            os.environ[t[0]] = t[1]
        elif type(t[1]) == int:
            os.environ[t[0]] = str(t[1])
        # file type
        elif type(t[1]):
            os.environ[t[0]] = t[1].name