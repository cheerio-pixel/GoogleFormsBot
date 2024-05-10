"""Script testing the functionality of the would-be bot
"""
from pathlib import Path
import random
from typing import Any
from google.oauth2 import service_account
from apiclient import discovery
import requests
import urllib.parse
import json

from pprint import pp

FORM_ID = "1meGKR3MJXPYkAw9KvNQB7yJSqbLA70ha2VvaHf28z28"
# SCOPES = ["https://www.googleapis.com/auth/forms.body.readonly"]
SCOPES = [
    "https://www.googleapis.com/auth/forms.responses.readonly",
    "https://www.googleapis.com/auth/forms.body.readonly",
]
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"
# CLIENT_SECRETS = Path("client_secrets.json")
SERVICE_KEY_FILE = Path("service_account_key.json")

URL_TEMPLATE = "https://docs.google.com/forms/d/e/{formId}/formResponse?&submit=Submit?usp=pp_url"


class Maybe:
    def __init__(self, value: Any | None):
        self.value = value

    def map(self, f):
        if self.value is None:
            return Maybe(None)
        else:
            return Maybe(f(self.value))

    def fmap(self, f):
        if self.value is None:
            return Maybe(None)
        else:
            return f(self.value)

    def is_empty(self):
        return self.value is None


class FormsAPI:
    def __init__(self, credentials):
        self._service = discovery.build(
            "forms",
            "v1",
            credentials=credentials,
            discoveryServiceUrl=DISCOVERY_DOC,
            static_discovery=False,
        )
        self.forms = self._service.forms


URL = URL_TEMPLATE.format(
    # This one requires the form id of the form that is sent to the user
    formId="1FAIpQLSd1r418uj0A8xH0qtZhtqFi6zM-hxMN1ebMnts-3uI9EjNghA"
)


"&entry.691441778=Option+4&entry.2133090356=Option+1&entry.2133090356=Option+3"
DATA_TEMPLATE = ["entry.691441778", "entry.2133090356"]
DATA_MAP = ["Option 4", ["Option 1", "Option 3"]]


# r = requests.post(URL, dict(zip(DATA_TEMPLATE, DATA_MAP)))
# print(r.status_code)

{
    "formId": "1meGKR3MJXPYkAw9KvNQB7yJSqbLA70ha2VvaHf28z28",
    "info": {
        "title": "Test form",
        "description": "Form to test",
        "documentTitle": "Untitled form",
    },
    "revisionId": "00000013",
    "responderUri": "https://docs.google.com/forms/d/e/1FAIpQLSd1r418uj0A8xH0qtZhtqFi6zM-hxMN1ebMnts-3uI9EjNghA/viewform",
    "items": [
        {
            "itemId": "6022a9c0",
            "title": "Radio button",
            "questionItem": {
                "question": {
                    "questionId": "29369072",
                    "choiceQuestion": {
                        "type": "RADIO",
                        "options": [
                            {"value": "Option 1"},
                            {"value": "Option 2"},
                            {"value": "Option 3"},
                            {"value": "Option 4"},
                            {"value": "Option 5"},
                        ],
                    },
                }
            },
        },
        {
            "itemId": "20d66054",
            "title": "Checkbox",
            "questionItem": {
                "question": {
                    "questionId": "7f246034",
                    "choiceQuestion": {
                        "type": "CHECKBOX",
                        "options": [
                            {"value": "Option 1"},
                            {"value": "Option 2"},
                            {"value": "Option 3"},
                            {"value": "Option 4"},
                            {"value": "Option 5"},
                        ],
                    },
                }
            },
        },
    ],
    "linkedSheetId": "1HMy1NYEJiNZGyVnFR-BX9jATEw_zhSSjP-jP1P7feFY",
}
# ["entry.691441778", "entry.2133090356"]

# Links question id to entry
QUESTION_ID_MAP = {
    "29369072": "entry.691441778",
    "7f246034": "entry.2133090356",
}


def get_item_type(item):
    """Assumming a question item, with choices, get the type"""
    return item["questionItem"]["question"]["choiceQuestion"]["type"]


def get_item_options(item):
    return item["questionItem"]["question"]["choiceQuestion"]["options"]


def _main():
    creds = (
        credentials
    ) = service_account.Credentials.from_service_account_file(
        SERVICE_KEY_FILE,
    ).with_scopes(
        SCOPES
    )
    api = FormsAPI(creds)
    responses_file = Path("responses.txt")
    if not responses_file.exists():
        with open(responses_file, "+w") as f:
            json.dump(
                api.forms()
                .responses()
                .list(formId=ORIGIN_EDIT_FORM_ID)
                .execute(),
                f,
            )

    ans = []
    with open(responses_file, "+r") as f:
        ans = json.load(f)

    responses: list = []
    for x in ans.get("responses"):
        # print(x.get("answers").values())
        # print()

        accum = []
        for k in SUBMISSION_ENTRY_MAP_WITH_QUESTION_ID.keys():
            accum.append(
                list(
                    map(
                        lambda x: x.get("value"),
                        x.get("answers")[k].get("textAnswers").get("answers"),
                    )
                )
            )
        responses.append(accum)
    for x in responses:
        print(x)
        print()
    # for x in responses:
    #     data = dict(zip(SUBMISSION_ENTRIES, x))
    #     r = requests.post(SUBMISSION_URL, data)
    #     if r.status >= 400:
    #         print("ERROR", r.status)


def _main():
    with open("RepuestasParaMigrar.csv") as f:
        for x in csv.reader(f):
            for k, v in zip(SUBMISSION_ENTRIES, x[2:]):
                print(k, v)

                print()
                print(v.split(", "))

            print()


def main():
    creds = (
        credentials
    ) = service_account.Credentials.from_service_account_file(
        SERVICE_KEY_FILE,
    ).with_scopes(
        SCOPES
    )
    api = FormsAPI(creds)
    form_file = Path("formSchema.txt")
    if not form_file.exists():
        with open(form_file, "+w") as f:
            json.dump(api.forms().get(formId=EDIT_FORM_ID).execute(), f)

    ans = []
    with open(form_file, "+r") as f:
        ans = json.load(f)

    options = ans.get("items")
    print(dict(zip(map(get_questionId, options), SUBMISSION_ENTRIES)))

    # for o in options:
    #     print(o["title"])
    #     print(get_options(o))


def _main():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_KEY_FILE,
    ).with_scopes(SCOPES)
    api = FormsAPI(credentials)
    result = (
        api.forms().responses().list(formId=FORM_ID, pageSize=400).execute()
    )
    previous_form_response = {q: [] for q in QUESTION_ID_MAP.values()}
    for question in QUESTION_ID_MAP.keys():
        # Filter empty replies
        for answer in filter(lambda x: x.get("answers"), result["responses"]):
            answer_list = answer["answers"][question]["textAnswers"]["answers"]

            previous_form_response[QUESTION_ID_MAP[question]].append(
                answer_list
            )

    to_send_form_response_data = {q: [] for q in QUESTION_ID_MAP.values()}
    for k, v in previous_form_response.items():
        random.choices(population=v, k=10)
        to_send_form_response_data[k] = random.choices(population=v, k=10)

    # Link
    # questionId -> entry

    # print(result)
    # result = api.forms().get(formId=FORM_ID).execute()
    # with open("FormStructure.txt", "+w") as f:
    #     f.write(json.dumps(result))
    # with open("FormStructure.txt", "+r") as f:
    #     result = json.load(f)
    # for item in result["items"]:
    #     print(get_item_type(item))


if __name__ == "__main__":
    main()
