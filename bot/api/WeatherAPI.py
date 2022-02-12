import requests
from urllib.parse import urlencode
from bot.api.WeatherExceptions import InvalidCityNameError, InvalidApiKeyError


class WeatherAPI:

    def __init__(self, api_key: str, city_name: str = "", base_url: str = "http://dataservice.accuweather.com",
                 language: str = "it-IT", details: bool = True):
        self.key = api_key
        self.cc = city_name
        self.base_url = base_url
        self.language = language
        self.details = str(details).lower()

        if city_name:
            try:
                int(city_name)
            except ValueError or TypeError:
                self.cc = self._get_code()

        if not self.cc or not self.key:
            print("WeatherAPI module not enabled")

    def _get_code(self):
        payload = {
            "apikey": self.key,
            "q": self.cc,
            "language": self.language
        }
        data = self._request(payload, "locations", "v1", "cities", "autocomplete", coderequest=True)

        if not data:
            raise InvalidCityNameError

        print("Your city key is {}, you can now edit your settings and put it instead of your city name".format(
            data[0]["Key"]))
        return data[0]["Key"]

    def _request(self, payload, *parameters, coderequest=False):
        payload = urlencode(payload)
        url = "{}/{}{}?{}".format(
            self.base_url,
            '/'.join(parameters),
            '/' + self.cc if not coderequest else '',
            payload
        )

        req = requests.post(url)

        if req.status_code == 401:
            raise InvalidApiKeyError

        return req.json()

    def _f_to_c(self, temp):
        return round((float(temp) - 32) * 5 / 9)

    def get_forecasts(self, beautify=True):
        if not self.cc or not self.key:
            return {
                "title": "Invalid Credentials",
                "forecast": "",
                "precipitations": "",
                "min_temp": "",
                "max_temp": "",
                "link": ""
            }
        payload = {
            "apikey": self.key,
            "language": self.language,
            "details": self.details
        }
        data = self._request(payload, "forecasts", "v1", "daily", "1day")
        try:
            forecasts = data["DailyForecasts"][0]  # forecasts/v1/daily/1day/
        except KeyError:
            forecasts = "Limit reached with Weather APIs"

        if beautify:
            return self._beautify(data)

        return {
            "title": data["Headline"]["Text"],

            "forecasts": "{}, {}".format(forecasts["Day"]["IconPhrase"],
                                         forecasts["Day"]["ShortPhrase"]),

            "precipitations": forecasts["Day"]["HasPrecipitation"],

            "min_temp": self._f_to_c(forecasts["Temperature"]["Minimum"]["Value"]),

            "max_temp": self._f_to_c(forecasts["Temperature"]["Maximum"]["Value"]),

            "link": data["Headline"]["Link"]
        }

    def _beautify(self, data):
        try:
            forecasts = data["DailyForecasts"][0]
        except KeyError:
            forecasts = "Limit reached with Weather APIs"

        base = '🌎 <a href="{}">{}</a>\n🗒 Dettagli: {}\n🌡 Temperatura: {}°C/{}°C\n🌧 Precipitazioni: {}'.format(
            data["Headline"]["Link"],
            forecasts["Day"]["ShortPhrase"],
            # data["Headline"]["Text"],
            forecasts["Day"]["IconPhrase"],
            str(self._f_to_c(forecasts["Temperature"]["Minimum"]["Value"])),
            str(self._f_to_c(forecasts["Temperature"]["Maximum"]["Value"])),
            "sì" if forecasts["Day"]["HasPrecipitation"] else "no"
        )

        return base
