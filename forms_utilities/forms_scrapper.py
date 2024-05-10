"""This whole method is completly unstable, since google developers may decide change their html structure
It may be much, much better to just use their api
"""
import requests
from bs4 import BeautifulSoup, NavigableString
import json
import re

VIEWFORM_URL_TEMPLATE = "https://docs.google.com/forms/d/e/{formId}/viewform"


def get_form_html(formId) -> tuple[str, int]:
    r = requests.get(VIEWFORM_URL_TEMPLATE.format(formId=formId))
    return r.text, r.status_code


def main():
    view_form_id = "1FAIpQLSeOp_6Ck80EDovHAdXteW8gWXYLjiVhtZY4izdJR2NkvYHqgA"
    html, error = get_form_html(view_form_id)
    if error != 200:
        # There is an error
        # But we don't notify this in more detail
        print("ERROR")

    form = FormHTML(html)

    data_array = form.question_data
    for data in data_array:
        print()

        print(data.entry_id)
        print(data.entry_name)
        print(data.entry_options)
        print()
        # print(data.entry_name)
        # print(data.entry_id)


class FormQuestionData:
    """The array that as of 3/11/2023 is in each question in the tag of "data-params" """

    def __init__(self, array):
        """Print this array to see the structure of the data"""
        self.array = array
        self._entry_options = None

    @property
    def entry_id(self):
        return self.array[0][4][0][0]

    @property
    def entry_id_name(self):
        """Entry id for submission"""
        return f"entry.{self.entry_id}"

    @property
    def entry_name(self):
        return self.array[0][1]

    @property
    def entry_options(self):
        if self._entry_options:
            return self._entry_options
        else:
            self._entry_options = []

        for opts in self.array[0][4]:
            for x in opts[1]:
                self._entry_options.append(x[0])

        return self._entry_options


class FormHTML:
    def __init__(self, html: str):
        self._html = html
        self._soup: BeautifulSoup = BeautifulSoup(html, features="lxml")
        self._question_data = None

    @property
    def question_data(self) -> list[FormQuestionData]:
        if self._question_data:
            return self._question_data
        params = self._soup.find_all("div", {"data-params": re.compile(r".*")})
        res = []
        for p in params:
            data_params = p.attrs.get("data-params")
            parseable = "[" + data_params[4:].strip()
            data_array = json.loads(parseable)
            res.append(FormQuestionData(data_array))
        self._question_data = res
        return res


if __name__ == "__main__":
    main()
