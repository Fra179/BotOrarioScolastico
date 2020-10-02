import os
from bot import Bot

token = os.getenv("TOKEN")
cvv_uname = os.getenv("CVV_UNAME")
cvv_passwd = os.getenv("CVV_PASSWD")
accu_weather_token = os.getenv("ACCU_WEATHER_TOKEN")

if token == "":
    raise Exception("Invalid Token")

print("Started")
Bot(token, cvv_uname, cvv_passwd, accu_weather_token).start()
