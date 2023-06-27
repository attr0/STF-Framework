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

from pathlib import Path

"""
Reference: https://www.cnblogs.com/ydf0509/p/16663158.html
"""
logger_config_template: dict = {
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
            'filename': '',
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
            'filename': '',
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

def get_logger_config(logdir: str, name: str) -> dict:
    config = logger_config_template.copy()
    config['handlers']['default_file']['filename'] = Path(logdir) / (name + '.process.log')
    config['handlers']['access_file']['filename'] = Path(logdir) / (name + '.access.log')
    return config