from config import *
from system import *
from dateutil import parser

import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

os.environ['conf'] = './core.toml'
load_configuration()

mf.init(core_config.listen_ip, core_config.dev, core_config.min_port)

s = System(logger, system_config_list[0])
s.init()

st = parser.parse("2022-05-01 00:00:00") 
ed = parser.parse("2022-05-01 00:12:00") 
c = s.predict(["TDS91006", "TDS90074", "TDS90063", "TDSTTR10003", "TDSTPR10011",  "TDSNCWBR10002"], 1, st, ed)
res = asyncio.run(c)

res = from_pandas_to_dict(res)
print(res)

s.shutdown()