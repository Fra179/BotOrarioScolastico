class InvalidApiKeyError(Exception):
    def __init__(self):
        self.message = "The API key you inserted isn't valid"


class InvalidCityNameError(Exception):
    def __init__(self):
        self.message = "Couldn't find any city with this name or code. Please check again."
