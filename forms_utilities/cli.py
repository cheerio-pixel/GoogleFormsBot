import argparse
from pathlib import Path

ARG_GOOGLE_API_PREFIX = "g-api-"


def get_args():
    parser = argparse.ArgumentParser(
        prog="Google Forms bot",
        description="A python script that let's you migrate google forms answers and generate responses from existing responses.",
    )

    parser.add_argument(
        "form-id",
        help="El id del formulario cuando lo envias a otras personas.",
    )

    subparser = parser.add_subparsers(
        help="sub-command help",
        required=True,
    )
    # parser_migrate = subparser.add_parser(
    #     "migrate",
    #     help="Copy responses from one form to another preserving some or all of the answers.",
    # )
    # parser_migrate.add_argument()

    parser_google_api_bot = subparser.add_parser(
        ARG_GOOGLE_API_PREFIX + "bot",
        help="Usa la api de google para frabircar y enviar respuestas usando las que ya estan.",
    )
    parser_google_api_bot.add_argument(
        "edit-form-id",
        required=True,
        help="El id del formulario cuando lo estas editando.",
        type=str,
    )
    parser_google_api_bot.add_argument(
        "-m",
        "--max-wait-minutes",
        default=0,
        help="El tiempo maximo de espera entre iteraciones.",
        type=int,
    )
    parser_google_api_bot.add_argument(
        "-k",
        "--group-count",
        default=10,
        help="El numero de respuetsas que habra en un grupo de respuestas.",
        dest="number_of_data",
        type=int,
    )
    parser_google_api_bot.add_argument(
        "-i",
        "--iterations",
        default=1,
        help="El numero de veces que enviar un grupo de respuestas.",
        type=int,
    )

    parser_scrapper_bot = subparser.add_parser(
        "alt-bot",
        help="Evita usar la api de google para fabricar y enviar respuestas.",
    )
    parser_scrapper_bot.add_argument(
        "csv-file",
        required=True,
        help="El archivo que obtienes descargando las repuestas de google forms.",
        type=Path,
    )

    parser_scrapper_bot.add_argument(
        "-k",
        "--count",
        default=10,
        help="El numero de respuestas que se enviaran.",
        dest="number_of_data",
        type=int,
    )
