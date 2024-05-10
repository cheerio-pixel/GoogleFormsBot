import os
from typing import Any, cast
from constants import DISCOVERY_DOC, SERVICE_KEY_FILE, SCOPES, get_project_root
from google.oauth2 import service_account
import json
from pathlib import Path
from apiclient import discovery


def get_service_credentials():
    return service_account.Credentials.from_service_account_file(
        SERVICE_KEY_FILE,
    ).with_scopes(SCOPES)


# It's preferible to model information, and thus use this class
# because it relies in the schema of the google api for forms
class Form:
    def __init__(self, form):
        "An auxiliary-object for the FormsAPI representing a schema forms"
        self._form = form
        self._items: list[FormQuestionItem | FormItem] = []
        self._questions: list[FormQuestionItem] = []

    @property
    def questions(self):
        if not self._questions:
            self._questions = cast(
                list[FormQuestionItem],
                list(
                    filter(
                        lambda x: isinstance(x, FormQuestionItem), self.items
                    )
                ),
            )
        return self._questions

    @property
    def items(self):
        if not self._items:
            for item in self._form.get("items"):
                # We have questionItem and the others, since I don't
                # need to deal with those, I will just place them
                # aside
                if item.get("questionItem"):
                    self._items.append(FormQuestionItem(item))
                else:
                    self._items.append(FormItem(item))
        return self._items


class FormQuestionItem:
    def __init__(self, question):
        self._question = question
        self._options = []

    @property
    def title(self):
        return self._question.get("title")

    @property
    def id(self):
        return (
            self._question.get("questionItem")
            .get("question")
            .get("questionId")
        )

    @property
    def options(self):
        if not self._options:
            self._options = list(
                map(
                    lambda x: x.get("value"),
                    self._question.get("questionItem")
                    .get("question")
                    .get("choiceQuestion")
                    .get("options"),
                )
            )
        return self._options


class FormItem:
    def __init__(self, item):
        self._item = item


class FormResponse:
    def __init__(self, response):
        "An auxiliary-object for the FormsAPI representing an invidual response"
        self._response = response
        self._answers = None

    @property
    def answers(self) -> dict[str, list[str]]:
        if self._answers is None:
            res = {}
            for k, v in self._response.get("answers").items():
                res[k] = list(
                    map(
                        lambda x: x.get("value"),
                        v.get("textAnswers").get("answers"),
                    )
                )
            self._answers = res
        return self._answers

    def order_by_questions(
        self, questions: list[FormQuestionItem]
    ) -> list[list[str]]:
        """Return answers by the order which they appear in questions"""
        return [self.answers[question.id] for question in questions]


class FormsAPI:
    def __init__(self, credentials, formId, make_cache=True):
        self._service = discovery.build(
            "forms",
            "v1",
            credentials=credentials,
            discoveryServiceUrl=DISCOVERY_DOC,
            static_discovery=False,
        )
        self._formId = formId
        self._form_file = (
            get_project_root()
            / Path("cache")
            / Path(self._formId + "_formSchema.txt")
        )
        self._responses_file = (
            get_project_root()
            / Path("cache")
            / Path(self._formId + "_responses.txt")
        )
        self._make_cache = make_cache

    def refresh_form_cache(self):
        os.remove(self._form_file)
        os.remove(self._responses_file)

    @property
    def form(self):
        """A Google Forms document."""
        if self._make_cache:
            if not self._form_file.exists():
                r = self._service.forms().get(formId=self._formId).execute()
                # Only write to file if it doesn't raise an exception
                with open(self._form_file, "+w") as f:
                    json.dump(r, f)

            with open(self._form_file, "+r") as f:
                return Form(json.load(f))
        else:
            return Form(
                self._service.forms().get(formId=self._formId).execute()
            )

    def _load_or_download_responses(self):
        # TODO: Deal with the nextPageToken.
        # For good reasons, responses can be divided into multiple
        # requests but this only happend for at most 5000 responses

        # If set, that means there is more, that is a way of checking
        if self._make_cache:
            if not self._responses_file.exists():
                r = (
                    self._service.forms()
                    .responses()
                    .list(formId=self._formId)
                    .execute()
                )
                with open(self._responses_file, "+w") as f:
                    json.dump(
                        r,
                        f,
                    )
            with open(self._responses_file, "+r") as f:
                r = json.load(f)
                if r.get("nextPageToken"):
                    print(
                        "Not all responses where retrived. nextPageToken feature still not implemented."
                    )
                return r.get("responses")
        else:
            r = (
                self._service.forms()
                .responses()
                .list(formId=self._formId)
                .execute()
            )
            if r.get("nextPageToken"):
                print(
                    "Not all responses where retrived. nextPageToken feature still not implemented."
                )
            return r.get("responses")

    @property
    def responses(self):
        return list(
            map(
                FormResponse,
                cast(list[Any], self._load_or_download_responses()),
            )
        )
