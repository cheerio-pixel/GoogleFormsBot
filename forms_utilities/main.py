import base64
from io import BytesIO
import random
import asyncio
from multiprocessing import Pool

import matplotx
import forms_utilities
import constants
import forms_api
import data_processing as dp
import matplotlib.pyplot as plt


# Google API: START
# Google API: END

# FORMS INFORMATION: BEGIN
# URL_TEMPLATE = "https://docs.google.com/forms/d/e/{formId}/formResponse?&submit=Submit?usp=pp_url"

# FORM_ID = "1FAIpQLSe4k9RIUeC_bNmEHM3BWYCTMp5hIpS07ZrKvyp1mPxaqn-ZRA"
# EDIT_FORM_ID = "1lwRRjjiQ4ABzYgAXpWPX5xW7z6fJogdoF_5QJRuT8HQ"
# ORIGIN_EDIT_FORM_ID = "1P8SMgjiSoGmYDPyv90cNeus0snL1LRiiLZGFI_Tz8_A"

# SUBMISSION_URL = URL_TEMPLATE.format(formId=FORM_ID)

# """ They are ordered by their position on the form.
# """
# SUBMISSION_ENTRIES = [
#     "entry.1009259295",
#     "entry.1073740503",
#     "entry.1468314261",
#     "entry.1696061242",
#     "entry.1835951891",
#     "entry.722251281",
#     "entry.1061728567",
#     "entry.1726972286",
#     "entry.1053780769",
#     "entry.720508707",
#     "entry.256378380",
#     "entry.695462376",
#     "entry.948707752",
#     "entry.1841754979",
#     "entry.1327437307",
#     "entry.1800315705",
#     "entry.1338419110",
#     "entry.515626984",
#     "entry.1615802948",
#     "entry.521201946",
#     "entry.439457421",
# ]


# SUBMISSION_ENTRY_MAP_WITH_QUESTION_ID = {
#     "3c28131f": "entry.1009259295",
#     "3ffffad7": "entry.1073740503",
#     "5784b295": "entry.1468314261",
#     "6517d73a": "entry.1696061242",
#     "6d6e6713": "entry.1835951891",
#     "2b0cae11": "entry.722251281",
#     "3f48b137": "entry.1061728567",
#     "66ef817e": "entry.1726972286",
#     "3ecf6b21": "entry.1053780769",
#     "2af21723": "entry.720508707",
#     "0f48060c": "entry.256378380",
#     "2973e9e8": "entry.695462376",
#     "388c21a8": "entry.948707752",
#     "6dc6f363": "entry.1841754979",
#     "4f1f15fb": "entry.1327437307",
#     "6b4ea339": "entry.1800315705",
#     "4fc6a7a6": "entry.1338419110",
#     "1ebbd7e8": "entry.515626984",
#     "604f3244": "entry.1615802948",
#     "1f10e91a": "entry.521201946",
#     "1a31968d": "entry.439457421",
# }

# FORMS INFORMATION: BEGIN


# def submit_bot_answers(number_of_data):
#     """number_of_data is a positive integer that tells how much data should prepare for sending"""
#     creds = service_account.Credentials.from_service_account_file(
#         SERVICE_KEY_FILE,
#     ).with_scopes(SCOPES)
#     api = FormsAPI(creds)

#     ans = api.get_answers(EDIT_FORM_ID, invalidate_cache=True)

#     responses = api.get_responses(ans)

#     bot_responses_rotated = [
#         random.choices(list_of_responses, k=number_of_data)
#         for list_of_responses in zip(*responses[::-1])
#     ]
#     # Responses to generate in this batch

#     bot_responses = list(zip(*bot_responses_rotated))
#     for response in bot_responses:
#         data = dict(zip(SUBMISSION_ENTRIES, response))
#         r = requests.post(SUBMISSION_URL, data)
#         if r.status_code >= 400:
#             print("ERROR", r.reason)
#         else:
#             print("SUCCESS")


# # Migrate from one to another
# def migrate():
#     creds = (
#         credentials
#     ) = service_account.Credentials.from_service_account_file(
#         SERVICE_KEY_FILE,
#     ).with_scopes(
#         SCOPES
#     )
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

HTML_IMG_BASE64 = "<img src='data:image/png;base64,{imageBytes}'>"


def main():
    # forms_utilities.batch_bot_answers(
    #     iterations=15,
    #     max_wait_minutes=15,
    #     number_of_data=10,
    #     form_id="1FAIpQLSe4k9RIUeC_bNmEHM3BWYCTMp5hIpS07ZrKvyp1mPxaqn-ZRA",
    #     edit_form_id="1lwRRjjiQ4ABzYgAXpWPX5xW7z6fJogdoF_5QJRuT8HQ",
    # )
    import time

    t_0 = time.time()
    t_loading_api_0 = time.time()
    api = forms_api.FormsAPI(
        credentials=forms_api.get_service_credentials(),
        formId="1lwRRjjiQ4ABzYgAXpWPX5xW7z6fJogdoF_5QJRuT8HQ",
    )
    t_loading_api_f = time.time()
    # api.refresh_form_cache()
    t_making_frequency_tables_0 = time.time()
    frequency_tables: list[
        dp.SuperSantosMachine
    ] = dp.SuperSantosMachine.from_forms_api(api)
    t_making_frequency_tables_f = time.time()

    t_computing_frequency_tables_and_making_graphs_0 = time.time()
    with Pool(64) as p:
        result = "".join(
            p.starmap(make_one_block_of_questions, enumerate(frequency_tables))
        )
    t_computing_frequency_tables_and_making_graphs_f = time.time()

    print(
        result,
        file=open(constants.get_project_root() / "cache/result.html", "+w"),
    )
    t_f = time.time()
    print("Total time:", t_f - t_0)
    print("Loading google api:", t_loading_api_f - t_loading_api_0)
    print(
        "Making super santos machine:",
        t_making_frequency_tables_f - t_making_frequency_tables_0,
    )
    print(
        "Computing and graphing:",
        t_computing_frequency_tables_and_making_graphs_f
        - t_computing_frequency_tables_and_making_graphs_0,
    )


def make_one_block_of_questions(k: int, df: dp.SuperSantosMachine) -> str:
    g = dp.Grapher(df)

    # matplotx.styles.challenger_deep
    # matplotx.styles.pitaya_smoothie["light"]
    with plt.style.context(matplotx.styles.challenger_deep):
        fig, ax = g.graph_bar_plot()
    fig.tight_layout()

    buffer = BytesIO()
    plt.axis("tight")
    fig.savefig(
        buffer,
        format="png",
        bbox_inches="tight",
    )
    result = ""
    result += f"<h1>{df.title}</h1>\n"
    result += "\n<h1>Tabla de frecuencia</h1>\n"
    result += dp.export_dataframe_to_html_with_sytle(df.frequency_table)
    result += "\n<br><br>\n"
    result += "\n<h1>Diagrama</h1>\n"
    result += HTML_IMG_BASE64.format(
        imageBytes=base64.b64encode(buffer.getvalue()).decode("utf-8")
    )
    result += "\n<br><br>\n"
    result += "\n<h1>Interpretacion</h1>\n"
    result += "\n<br><br>\n"
    # Close the figure after using it
    plt.close(fig)
    return result


# def _main():
#     creds = (
#         credentials
#     ) = service_account.Credentials.from_service_account_file(
#         SERVICE_KEY_FILE,
#     ).with_scopes(
#         SCOPES
#     )
#     api = FormsAPI(
#         creds,
#         "1lwRRjjiQ4ABzYgAXpWPX5xW7z6fJogdoF_5QJRuT8HQ",
#     )
#     for x in api.responses:
#         print(x.order_by_questions(api.form.questions))


if __name__ == "__main__":
    main()
    # main()
    # submit_bot_answers(20)
