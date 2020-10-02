from json import loads
from datetime import datetime, timedelta
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup


class AuthenticationFailedError(Exception):
    def __init__(self):
        self.message = "Invalid username or password"


class ClasseVivaAgendaAPI:
    baseApiUrl = "https://web.spaggiari.eu/"

    def __init__(self):
        self.id = None
        self.token = None

    def login(self, username: str, password: str):
        url = self.baseApiUrl + "auth-p7/app/default/AuthApi4.php?a=aLoginPwd"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "uid": username,
            "pwd": password
        }
        r = requests.post(url, data, headers=headers)

        if "Identificativo o password errati" in r.text:
            return False

        self.token = r.cookies.get_dict().get("PHPSESSID", "")
        self.id = loads(r.text)["data"]["auth"]["accountInfo"]["id"]

        return True

    def logout(self):
        self.token = None

    def _request(self, path):
        url = self.baseApiUrl + path

        headers = {"Cookie": "PHPSESSID=" + self.token}
        req = requests.get(url, headers=headers)

        if "Password dimenticata?" in req.text:
            return False

        return req.content

    def format_agenda(self, data):
        from datetime import datetime
        if (data is None) or (not data.get('agenda')):
            return "\n🗓 L'agenda è ancora vuota."

        result = ""
        first_event = True
        events_list = data['agenda']
        events_list.sort(key=lambda x: str(x['evtDatetimeBegin']).split("T", 1)[0])
        for event in events_list:
            date = str(event['evtDatetimeBegin']).split("T", 1)[0]
            date = date.split("-", 2)
            today = datetime.now().day
            evtDay = int(date[2])

            if evtDay != today:
                evt_type = "📌" if event['evtCode'] == "AGNT" else "📝"
                separator = "\n" if first_event else "\n\n\n"
                first_event = False
                result += separator + "{0} {1}/{2}/{3} • <b>{4}</b>\n{5}".format(evt_type, date[0], date[1], date[2],
                                                                                 event['authorName'].title(),
                                                                                 event['notes'])
        return result

    def parse_xml(self, xml):

        if b"Nessun dato da esportare!" in xml:
            return self.format_agenda({})

        if not xml:
            return self.format_agenda({})

        s = BeautifulSoup(xml, "xml")
        row = s.find_all("Row")
        del row[0]

        useless_part = [
            "<ss:Cell>",
            "<ss:Data ss:Type=\"String\">",
            "</ss:Data>",
            "</ss:Cell>",
            "<ss:Data ss:Type=\"String\"/>"

        ]

        parsed = []

        for x in row:

            x = list(filter(lambda y: y != "\n" and useless_part[4] not in y, x))

            for y in range(len(x)):
                for z in useless_part:
                    x[y] = str(x[y]).replace(z, "")

            parsed.append(x)

        d = [
            {
                "evtDatetimeBegin": '-'.join(x[1].split("-")[::-1]),
                "evtCode": x[12],
                "authorName": x[7],
                "notes": x[10]
            } for x in parsed
        ]

        return self.format_agenda({"agenda": d})

    def agenda(self, days: int = 14):
        start_time = datetime.now()
        end_time = start_time + timedelta(days=days)

        parameters = {
            "tipo": "agenda",
            "autore_id": self.id,
            "tipo_export": "EVENTI_AGENDA_STUDENTI",
            "dal": start_time.strftime("%Y-%m-%d"),
            "al": end_time.strftime("%Y-%m-%d")
        }

        re = self._request("fml/app/default/xml_export.php?" + urlencode(parameters))
        return self.parse_xml(re)
