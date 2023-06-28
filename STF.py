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
import uvicorn
import os
import traceback

"""
Parse CMD config
"""
class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise Exception(message)
    
cmdArgs: argparse.Namespace
cmdParser = ThrowingArgumentParser(prog='STF Core')
cmdParser.add_argument('-c', '--conf', type=argparse.FileType('rb'), 
                       help="configuration file", required=True)
cmdParser.add_argument('-ip', help="listened ip", default="127.0.0.1")
cmdParser.add_argument('-port', type=int, help="listened port", default=8080)

def arg_to_env(args: argparse.Namespace):
    os.environ['conf'] = args.conf.name


logger_config: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s %(levelprefix)s %(message)s",
            "use_colors": False,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
            "use_colors": False,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "default_file": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            'filename': './stf.process.log',
            'maxBytes': 100 * 1024 * 1024,
            'backupCount': 3,
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access_file": {
            "formatter": "access",
            "class": "logging.handlers.RotatingFileHandler",
            'filename': './stf.access.log',
            'maxBytes': 100 * 1024 * 1024,
            'backupCount': 3,
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default", "default_file"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access", "access_file"], "level": "INFO", "propagate": False},
    },
}

if __name__ == "__main__":
    try:
        cmdArgs = cmdParser.parse_args()
        arg_to_env(cmdArgs)

        uvicorn.run(
            "web:app",
            host=cmdArgs.ip, 
            port=cmdArgs.port, 
            reload=False, 
            log_config=logger_config,
            lifespan='on',
            app_dir="./core",
        )
    except Exception as e:
        with open('panic.log', 'a') as f:
            f.write("\n=======================================\n")
            f.write("<<<<STF-Core Launch Failed>>>>\n")
            traceback.print_exc(limit=1, file=f)
            f.flush()
            traceback.print_exc(limit=1)