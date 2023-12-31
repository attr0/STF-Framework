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

from config import *
from logger import *

import uvicorn
import os
import sys
import traceback

if __name__ == "__main__":
    try:
        cmdArgs = cmdParser.parse_args()
        arg_to_env(cmdArgs)
        logger_config = get_logger_config()

        uvicorn.run(
            "web:app",
            host=cmdArgs.ip, 
            port=cmdArgs.port, 
            reload=False, 
            log_config=logger_config,
            lifespan='on'
            )
    except Exception as e:
        with open('panic.log', 'a') as f:
            f.write("\n=======================================\n")
            f.write(f"<<<<NODE Launch Error>>>>\n")
            traceback.print_exc(limit=1, file=f)
            f.flush()