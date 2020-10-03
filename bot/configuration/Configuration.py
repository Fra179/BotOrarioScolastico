import json
from datetime import datetime
from bot.database.DBUtils import DBUtils
from bot.api.WeatherAPI import WeatherAPI


class ConfigurationNotExistingException(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidConfigurationException(Exception):
    def __init__(self, message):
        super().__init__(message)


class Configuration:
    def __init__(self, db_utils: DBUtils, enable_cvv: bool = False):
        self._data = None
        self._city_code = None
        self._cvv_enabled = enable_cvv
        self._start_message = None
        self._school_day_message = None
        self._free_day_message = None
        self._info = None
        self._subjects_schedule = None
        self._enable_gm = None
        self._notification_time = None
        self._days_translation = {}
        self._all_subjects = []
        self._working_days = []
        self._db_utils = db_utils
        self.w = None
        self.load_config()

    def attach_weather(self, weather: WeatherAPI):
        self.w = weather

    @property
    def city_code(self):
        return self._city_code

    @city_code.setter
    def city_code(self, new_id: int):
        print(f"Setted {new_id}")

    @property
    def notification_time(self):
        return self._notification_time

    @notification_time.setter
    def notification_time(self, new_time: int):
        print(f"Setted {new_time}")

    @property
    def enable_gm(self):
        return self._enable_gm

    @enable_gm.setter
    def enable_gm(self, new_status: bool):
        with open("configuration.json", "w") as f:
            self._data["enable_gm"] = new_status
            self._enable_gm = new_status
            json.dump(self._data, f, indent=2)

    @property
    def start_message(self):
        return self._start_message

    @start_message.setter
    def start_message(self, message: str):
        print(f"Setted {message}")

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, new_info: str):
        print(f"Setted {new_info}")

    @property
    def school_day_message(self):
        return self._school_day_message

    @school_day_message.setter
    def school_day_message(self, message: str):
        print(f"Setted {message}")

    @property
    def free_day_message(self):
        return self._free_day_message

    @free_day_message.setter
    def free_day_message(self, message: str):
        print(f"Setted {message}")

    @property
    def days_translation(self):
        return self._days_translation

    @property
    def subjects_schedule(self):
        return self._subjects_schedule

    @property
    def working_days(self):
        return self._working_days

    @property
    def all_subjects(self):
        return self._all_subjects

    def _validate_config(self, config: dict):
        # Config validation
        if not config.get("messages"):
            raise InvalidConfigurationException("Messages missing.")
        if not config.get("days_translation") or len(config.get("days_translation")) != 7:
            raise InvalidConfigurationException("Days translation missing.")
        if not config["messages"].get("start"):
            raise InvalidConfigurationException("Missing start message")
        if not config["messages"].get("info"):
            raise InvalidConfigurationException("Missing info message")
        try:
            config["enable_gm"]
        except KeyError:
            raise InvalidConfigurationException("Missing enable_gm")
        if not config.get("notification_time"):
            raise InvalidConfigurationException("Missing notification time")
        if not config["messages"].get("school_day"):
            raise InvalidConfigurationException("Missing school day message")
        if not config["messages"].get("free_day"):
            raise InvalidConfigurationException("Missing free day message")
        if not config.get("subjects_schedule"):
            raise InvalidConfigurationException("Missing subjects schedule")

    def load_config(self):
        try:
            with open("configuration.json", "r", encoding="utf-8") as f:
                self._data = json.load(f)
        except FileNotFoundError as e:
            raise ConfigurationNotExistingException(e)

        self._validate_config(self._data)
        self._start_message = self._data["messages"]["start"]
        self._enable_gm = self._data.get("enable_gm", False)
        self._school_day_message = self._data["messages"]["school_day"]
        self._free_day_message = self._data["messages"]["free_day"]
        self._notification_time = datetime.strptime(self._data["notification_time"], "%H:%M")
        self._info = self._data["messages"]["info"]
        self._days_translation = self._data["days_translation"]
        self._subjects_schedule = {k: v for k, v in self._data["subjects_schedule"].items() if
                                   k in self._days_translation.keys() and len(v) > 0}
        self._city_code = self._data.get("city_code")

        for _, v in self._subjects_schedule.items():
            for m in v:
                sub = m.split("(")[0].strip()
                if sub not in self._all_subjects:
                    self._all_subjects.append(m.split("(")[0].strip())

        self._working_days = [k for k, _ in self._subjects_schedule.items()]

    def get_parsed_subjects_schedule(self, day: str = "") -> str:
        if not day:
            day = datetime.now().strftime('%a').lower()

        schedule = self._subjects_schedule
        if day not in self._days_translation.keys() or day not in schedule.keys():
            return "Not a valid day"

        return "\n".join(f"{x}) {y}" for x, y in enumerate(schedule[day], start=1))

    def get_formatted_message(self, message: str, chat_id: int):
        name, username = self._db_utils.get_user_info(chat_id)

        params = [
            ("{username}", username),
            ("{name}", name),
            ("{weather}", self.w.get_forecasts),
            ("{day}", self._days_translation[datetime.now().strftime('%a').lower()]),
            ("{subjects_schedule}", self.get_parsed_subjects_schedule)
        ]

        for k, v in params:
            if callable(v):
                v = v()
            message = message.replace(k, v)

        return message
