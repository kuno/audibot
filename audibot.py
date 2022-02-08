import os
import pprint
import audible
from simplegmail import Gmail
from jinja2 import Environment, PackageLoader, select_autoescape
env = Environment(
    loader=PackageLoader("audibot"),
    autoescape=select_autoescape()
)

USERNAME = ""
PASSWORD = ""
COUNTRY_CODE = "us"
COLLECTION_ID = '942f9150-c09c-4e05-81ac-3ea3dc1ecb45'

SENDER = "neokuno@gmail.com"
TO = 'customersupport@audible.com'
SUBJECT = "Please help return these books"
UPPER_LIMIT_TO_RETURN = 3


def get_number_to_return():
    try:
        return int(os.getenv("NUMBER_TO_RETURN"))
    except:
        return UPPER_LIMIT_TO_RETURN


def get_ready_to_return_library_items():
    auth = audible.Authenticator.from_file('./audible_auth.json')
    with audible.Client(auth=auth) as client:
        library = client.get("/1.0/library")
        library_items = [item for item in library["items"]]
        ready_to_return = client.get(f"/1.0/collections/{COLLECTION_ID}/items")
        ready_to_return_items = [item for item in ready_to_return["items"]]

        return [
            li
            for li in library_items
            for ri in ready_to_return_items
            if li['asin'] == ri['asin']
        ]


def send_email(items):
    pp = pprint.PrettyPrinter(indent=4)
    gmail = Gmail()
    html_template = env.get_template("mail.html")
    msg_html = html_template.render(items=items)
    text_template = env.get_template("mail.txt")
    msg_plain = text_template.render(items=items)
    params = {
        "to": TO,
        "sender": SENDER,
        "subject": SUBJECT,
        "msg_html": msg_html,
        "msg_plain": msg_plain,
        "signature": True  # use my account signature
    }
    pp.pprint(params)
    message = gmail.send_message(**params)
    pp.pprint(message)


if __name__ == '__main__':
    ntr = get_number_to_return()
    ready_to_return_library_items = get_ready_to_return_library_items()
    items = ready_to_return_library_items[:ntr]

    #
    if len(items) > 0 and len(items) <= UPPER_LIMIT_TO_RETURN:
        send_email(items)
