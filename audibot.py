import os
import pprint
import audible
from simplegmail import Gmail
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(loader=PackageLoader("audibot"), autoescape=select_autoescape())

COUNTRY_CODE = "us"
TO = "customersupport@audible.com"
SUBJECT = "Please help return these books"
UPPER_LIMIT_TO_RETURN = 3

pp = pprint.PrettyPrinter(indent=4)


def get_number_to_return():
    try:
        return int(os.getenv("NUMBER_TO_RETURN"))
    except:
        return UPPER_LIMIT_TO_RETURN


def get_collection_id(auth, collection_name):
    with audible.Client(auth=auth) as client:
        collections = client.get("/1.0/collections")
        results = list(
            filter(
                lambda col: col["name"] == collection_name, collections["collections"]
            )
        )

        if len(results) > 0:
            return results[0]["collection_id"]
        else:
            return None


def get_ready_to_return_library_items(auth, collection_id):
    with audible.Client(auth=auth) as client:
        library = client.get("/1.0/library")
        library_items = [item for item in library["items"]]
        ready_to_return = client.get(f"/1.0/collections/{collection_id}/items")
        ready_to_return_items = [item for item in ready_to_return["items"]]

        return [
            li
            for li in library_items
            for ri in ready_to_return_items
            if li["asin"] == ri["asin"]
        ]


def send_email(items, gmail_sender):
    gmail = Gmail()
    html_template = env.get_template("mail.html")
    msg_html = html_template.render(items=items)
    text_template = env.get_template("mail.txt")
    msg_plain = text_template.render(items=items)
    params = {
        "to": TO,
        "sender": gmail_sender,
        "subject": SUBJECT,
        "msg_html": msg_html,
        "msg_plain": msg_plain,
        "signature": True,  # use my account signature
    }
    pp.pprint(params)
    message = gmail.send_message(**params)
    pp.pprint(message)


if __name__ == "__main__":
    #
    collection_name = os.getenv("COLLECTION_NAME")
    gmail_sender = os.getenv("GMAIL_SENDER")

    if collection_name is not None and gmail_sender is not None:
        auth = audible.Authenticator.from_file("./audible_auth.json")
        collection_id = get_collection_id(auth, collection_name)
        ready_to_return_library_items = get_ready_to_return_library_items(
            auth, collection_id
        )

        number_to_return = get_number_to_return()

        #
        if UPPER_LIMIT_TO_RETURN >= number_to_return > 0:
            send_email(ready_to_return_library_items[0:number_to_return], gmail_sender)

        else:
            pp.pprint(
                f"number to return: {number_to_return} is not in the range of 1~{UPPER_LIMIT_TO_RETURN}"
            )
    else:
        pp.pprint("Please set environment variables COLLECTION_NAME and GMAIL_SENDER")
