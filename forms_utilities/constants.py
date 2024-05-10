from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).absolute().parent.parent


SCOPES = [
    "https://www.googleapis.com/auth/forms.responses.readonly",
    "https://www.googleapis.com/auth/forms.body.readonly",
]
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"
SERVICE_KEY_FILE = get_project_root() / Path(
    "resources/json/service_account_key.json"
)

SUBMISSION_URL_TEMPLATE = "https://docs.google.com/forms/d/e/{formId}/formResponse?&submit=Submit?usp=pp_url"
