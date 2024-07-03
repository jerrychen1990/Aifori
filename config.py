from os import curdir
import os
from loguru import logger

voice_dir = curdir + "/voices"
os.makedirs(voice_dir, exist_ok=True)


log_file = "logs/detail.log"
logger.add(log_file, rotation="00:00", retention="7 days", level="DEBUG")


group_id = "1805897497076318387"
api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJoYW8iLCJVc2VyTmFtZSI6ImhhbyIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxODA1ODk3NDk3MDg0NzA2OTk1IiwiUGhvbmUiOiIxNTI2ODE4NDY4NCIsIkdyb3VwSUQiOiIxODA1ODk3NDk3MDc2MzE4Mzg3IiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoiIiwiQ3JlYXRlVGltZSI6IjIwMjQtMDctMDMgMTA6Mjg6NDEiLCJpc3MiOiJtaW5pbWF4In0.f_zrm2WU6IQ1U1-a_6NEEkIg2fQtuwQeOUWGD2UtRnkD1_h2dygYZ450ZU6tp3TKLSogkvF2Xa0xIEb6I-CzFpDTrSj17sncQcGaLXMZJqtGjw68ur7w8FSfczeCO9UVkDBSagdOkdh2C7Iq7uRGiZiJ1oT-CYagOoWCO0Ha-cdbHN6GRMLIOwm7bp5D2aEXJcO1ZJmDxCGtRWlfY8SZVfdQGk5VsNLokDKWj1dSvTjPqIdJQssHWmDoisLPb1FUrxcfFP7yPwMrhrts9e6zZGYoSxaa0ucSH-KnAnRg9dskCRTKU5GECJRLcEiccqSiSEemXA86EWForeS9D3hY4g"


character_map = {
    "甜心小玲": {
        "voice_id": "tianxin_xiaoling",
        "desc": "一个可爱、甜美、活泼的女生，声音甜美而治愈。"

    },
    "淡雅学姐": {
        "voice_id": "danya_xuejie",
        "desc": "一个优雅、知性、成熟的女性，声音温柔而坚定。"
    },
    "俊朗男友": {
        "voice_id": "junlang_nanyou",
        "desc": "一个阳光、帅气、充满自信的男生，声音温暖而磁性。"
    },
    "霸道少爷": {
        "voice_id": "badao_shaoye",
        "desc": "一个霸气、自信、帅气的男生，声音低沉而有力。"
    }
}
