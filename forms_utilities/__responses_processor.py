from collections import Counter
from functools import reduce, partial
from io import BytesIO
from pathlib import Path
from time import sleep
import pandas as pd
from constants import get_project_root, SUBMISSION_URL_TEMPLATE
import re
import random
import requests
import matplotlib.pyplot as plt
import base64
import matplotx
import textwrap

from multiprocessing import Pool

import forms_scrapper as fs
import data_processing as dp


# TEST_FILE = Path("Preferencias de Software - FINAL.csv")
# TEST_FILE = Path(get_project_root() / "resources/csv/Favor.csv")
TEST_FILE = Path(get_project_root() / "resources/csv/Vladimir.csv")

if not TEST_FILE.exists:
    raise FileNotFoundError(f"{TEST_FILE} should exist in testing")


HTML_IMG_BASE64 = "<img src='data:image/png;base64,{imageBytes}'>"


def submit_bots(number_of_data=1):
    view_form_id = "1FAIpQLSc2HBsuc-olZAsmCLJ3jnE6RMiDzWl0-iOvV233MVQr6O7G3w"
    html, error = fs.get_form_html(view_form_id)
    if error != 200:
        # There is an error
        # But we don't notify this in more detail
        print("ERROR")

    form = fs.FormHTML(html)

    data_array = form.question_data
    df = pd.read_csv(TEST_FILE)

    separated = []
    for data in data_array:
        # print("(" + "|".join(map(re.escape, data.entry_options)) + ")")
        # print(
        #     df[data.entry_name]
        #     .astype("str")
        #     .map(
        #         re.compile(
        #             "(" + "|".join(map(re.escape, data.entry_options)) + ")"
        #         ).findall
        #     )
        # )
        separated.append(
            df[data.entry_name]
            .fillna("")
            .astype("str")
            .replace(r"\.0$", "", regex=True)
            # .astype("str")
            # .map(
            #     re.compile(
            #         "(" + "|".join(map(re.escape, data.entry_options)) + ")"
            #     ).findall
            # )
        )
    submission_entries = [x.entry_id_name for x in data_array]
    by_individuals = list(zip(*map(lambda x: x.to_list(), separated)))

    responses = by_individuals

    # Fabricate data based on previous responses
    bot_responses_rotated = [
        random.choices(list_of_responses, k=number_of_data)
        for list_of_responses in zip(*responses[::-1])
    ]

    # HTTP POST request with fabricated data

    for response in zip(*bot_responses_rotated):
        sleep(1)
        request_submit(submission_entries, view_form_id, response)
    # with Pool(64) as p:
    #     p.map(
    #         partial(request_submit, submission_entries, view_form_id),
    #         list(zip(*bot_responses_rotated)),
    #     )

    # data = dict(
    #     # zip(submission_entries, response),
    #     filter(
    #         lambda x: x[1],
    #         zip(submission_entries, response),
    #     )
    # )

    # # print(SUBMISSION_URL_TEMPLATE.format(formId=view_form_id))
    # r = requests.post(
    #     SUBMISSION_URL_TEMPLATE.format(formId=view_form_id), data
    # )

    # print(data)
    # if r.status_code >= 400:
    #     print(
    #         r.content,
    #         file=open(get_project_root() / "cache/response.html", "+w"),
    #     )
    #     print("ERROR", r.reason)
    # else:
    #     print("SUCCESS")


def request_submit(submission_entries, view_form_id, bot_response):
    data = dict(
        # zip(submission_entries, response),
        filter(
            lambda x: x[1],
            zip(submission_entries, bot_response),
        )
    )

    # print(SUBMISSION_URL_TEMPLATE.format(formId=view_form_id))
    r = requests.post(
        SUBMISSION_URL_TEMPLATE.format(formId=view_form_id), data
    )

    print(data)
    if r.status_code >= 400:
        print(
            r.content,
            file=open(get_project_root() / "cache/response.html", "+w"),
        )
        print("ERROR", r.reason)
    else:
        print("SUCCESS")


def _main():
    # view_form_id = "1FAIpQLSe4k9RIUeC_bNmEHM3BWYCTMp5hIpS07ZrKvyp1mPxaqn-ZRA"
    # html, error = fs.get_form_html(view_form_id)
    # if error != 200:
    #     # There is an error
    #     # But we don't notify this in more detail
    #     print("ERROR")

    # form = fs.FormHTML(html)

    # data_array = form.question_data

    df = pd.read_csv(TEST_FILE)
    # print(df)
    data = []

    result = ""
    for x in df.drop("Marca temporal", axis=1):
        title = x.split("\n")[-1]
        frequency_data = Counter(
            df[x]
            .map(lambda x: x[3:])
            .map(lambda x: "\n".join(textwrap.wrap(x, width=40)))
            .to_list()
        )
        machine = dp.SuperSantosMachine(title, frequency_data=frequency_data)
        with plt.style.context(matplotx.styles.dracula):
            fig, ax = dp.Grapher(machine).graph_pie_plot()
        buffer = BytesIO()
        fig.savefig(buffer, format="png", bbox_inches="tight")

        result += f"<h1>{title}</h1>\n"
        result += "\n<h1>Tabla de frecuencia</h1>\n"
        result += dp.export_dataframe_to_html_with_sytle(
            machine.frequency_table
        )
        result += "\n<br><br>\n"
        result += "\n<h1>Diagrama</h1>\n"
        result += HTML_IMG_BASE64.format(
            imageBytes=base64.b64encode(buffer.getvalue()).decode("utf-8")
        )
        plt.close(fig)
    print(
        result,
        file=open(get_project_root() / "cache/favorResult.html", "+w"),
    )

    # separated = []
    # for data in data_array:
    #     separated.append(
    #         df[data.entry_name].astype(str).map(
    #             re.compile(
    #                 "(" + "|".join(map(re.escape, data.entry_options)) + ")"
    #             ).findall
    #         ).to_list()
    #     )
    # print(list(zip(*separated)))


# def submit_bot_answers(number_of_data):
#     view_form_id = "1FAIpQLSe4k9RIUeC_bNmEHM3BWYCTMp5hIpS07ZrKvyp1mPxaqn-ZRA"
#     html, error = fs.get_form_html(view_form_id)
#     if error != 200:
#         # There is an error
#         # But we don't notify this in more detail
#         print("ERROR")

#     form = fs.FormHTML(html)

#     data_array = form.question_data

#     df = pd.read_csv(TEST_FILE)

#     # Generate entry list
#     submission_entries = [x.entry_id_name for x in data_array]

#     # Separate multivalued columns
#     separated = []
#     for data in data_array:
#         separated.append(
#             df[data.entry_name].map(
#                 re.compile(
#                     "(" + "|".join(map(re.escape, data.entry_options)) + ")"
#                 ).findall
#             )
#         )
#     by_individuals = list(zip(*map(lambda x: x.to_list(), separated)))

#     responses = by_individuals

#     # Fabricate data based on previous responses
#     bot_responses_rotated = [
#         random.choices(list_of_responses, k=number_of_data)
#         for list_of_responses in zip(*responses[::-1])
#     ]

#     # HTTP POST request with fabricated data
#     for response in zip(*bot_responses_rotated):
#         data = dict(zip(submission_entries, response))
#         r = requests.post(SUBMISSION_URL, data)
#         if r.status_code >= 400:
#             print("ERROR", r.reason)
#         else:
#             print("SUCCESS")


if __name__ == "__main__":
    # submit_bot_answers(5)
    submit_bots(137)
