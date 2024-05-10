from pathlib import Path
import re
from google.oauth2 import service_account
import random
import requests
import pandas as pd

import schedule
import time

import forms_api
import forms_scrapper as fs
from constants import SERVICE_KEY_FILE, SCOPES, SUBMISSION_URL_TEMPLATE


def batch_bot_answers(
    iterations: int,
    max_wait_minutes: int,
    number_of_data: int,
    form_id: str,
    edit_form_id: str | None = None,
    responses_csv: Path | None = None,
):
    """Iterations: the number of number_of_date to send.
    wait_time: The interval of time to wait between sending responses
    number_of_data: The number of date to send between each batch
    form_id: The id of the form that you send to users
    edit_form_id: The id of the form that you find when editing
    responses_csv: Path to the csv responses

    Note: if responses_csv is not specified, then edit_form_id must be
    specified and vice-versa.
    """

    for _ in range(iterations):
        submit_bot_answers(
            number_of_data,
            form_id,
            edit_form_id,
            responses_csv,
        )
        if max_wait_minutes > 0:
            time.sleep(60 * random.randint(1, max_wait_minutes))


def submit_bot_answers(
    number_of_data: int,
    form_id: str,
    editFormId: str | None = None,
    responses_csv: Path | None = None,
) -> str:
    """number_of_data is a positive integer that tells how much data should prepare for sending"""

    # ans = api.get_answers(EDIT_FORM_ID, invalidate_cache=True)

    # responses = api.get_responses(ans)

    html, error_code = fs.get_form_html(form_id)
    if error_code >= 400:
        return f"Couldn't download form html. Error code {error_code}"
    form = fs.FormHTML(html)

    responses = []

    if not responses_csv:
        api = forms_api.FormsAPI(
            forms_api.get_service_credentials(), editFormId, make_cache=False
        )
        responses = [
            res.order_by_questions(api.form.questions) for res in api.responses
        ]
    else:
        responses = csv_to_responses(responses_csv, form.question_data)

    bot_responses_rotated = [
        random.choices(list_of_responses, k=number_of_data)
        for list_of_responses in zip(*responses[::-1])
    ]

    submission_entries = list(
        map(lambda x: x.entry_id_name, form.question_data)
    )
    submission_url = SUBMISSION_URL_TEMPLATE.format(formId=form_id)
    # Responses to generate in this batch

    bot_responses = list(zip(*bot_responses_rotated))
    for response in bot_responses:
        data = dict(zip(submission_entries, response))
        r = requests.post(submission_url, data)
        if r.status_code >= 400:
            print("ERROR", r.reason)
        else:
            print("SUCCESS")
    return "Success"


def csv_to_responses(
    responses_csv: Path, data_array: list[fs.FormQuestionData]
) -> list[list[str]]:
    df = pd.read_csv(responses_csv)
    separated = []
    for data in data_array:
        separated.append(
            df[data.entry_name].map(
                re.compile(
                    "(" + "|".join(map(re.escape, data.entry_options)) + ")"
                ).findall
            )
        )
    return list(zip(*map(lambda x: x.to_list(), separated)))


# # Migrate from one to another
# def migrate():
#     creds = forms_api.get_service_credentials()
#     api = FormsAPI(creds)

#     ans = api.get_answers(ORIGIN_EDIT_FORM_ID)

#     schema = api.get_schema(EDIT_FORM_ID)

#     responses = api.get_responses(ans)

#     options = schema.get("items")

#     listing_of_options = [api.get_options(o) for o in options]
#     # print(listing_of_options)
#     # print()
#     # print()
#     # print(responses)
#     cleaned_responses = []
#     # Clean responses
#     for response in responses:
#         accum = []
#         # For each response, there is a list of possible values
#         for valid, answers in zip(listing_of_options, response):
#             valid_accum = []
#             for curr in answers:
#                 if curr in valid:
#                     valid_accum.append(curr)
#                 else:
#                     valid_accum.append(random.choice(valid))
#             accum.append(valid_accum)
#         cleaned_responses.append(accum)
#     for response in cleaned_responses:
#         data = dict(zip(SUBMISSION_ENTRIES, response))
#         r = requests.post(SUBMISSION_URL, data)
#         if r.status_code >= 400:
#             print("ERROR", r.status_code)
#         else:
#             print("SUCCESS")
