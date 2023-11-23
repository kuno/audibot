import os
import pprint
import audible
from simplegmail import Gmail
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(loader=PackageLoader("audibot"),
                  autoescape=select_autoescape())

COUNTRY_CODE = "us"
TO = "customersupport@audible.com"
SUBJECT = "Please help return these books"
UPPER_LIMIT_TO_RETURN = 3

pp = pprint.PrettyPrinter(indent=4)


def get_credential_dir():
    try:
        return int(os.getenv("CRE"))
    except:
        return UPPER_LIMIT_TO_RETURN


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


def send_email(client_secret_file, gmail_token_file, items, gmail_sender):
    gmail = Gmail(
        client_secret_file=client_secret_file,
        creds_file=gmail_token_file
    )
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

    if os.getenv("DRY_RUN") != "true":
        message = gmail.send_message(**params)
        pp.pprint(message)
    else:
        print("DRY RUN: not sending email")


if __name__ == "__main__":
    #
    gmail_token_file = os.getenv("GMAIL_TOKEN_FILE")
    client_secret_file = os.getenv("GMAIL_CLIENT_SECRET_FILE")
    audible_auth_file = os.getenv("AUDIBLE_AUTH_FILE")

    collection_name = os.getenv("COLLECTION_NAME")
    gmail_sender = os.getenv("GMAIL_SENDER")

    if collection_name is not None and gmail_sender is not None:
        print("Collection name and gmail sender are set")
        print(collection_name)
        print(gmail_sender)
        auth = audible.Authenticator.from_file(audible_auth_file)
        collection_id = get_collection_id(auth, collection_name)
        if collection_id is not None:
            ready_to_return_library_items = get_ready_to_return_library_items(
                auth, collection_id
            )

            number_to_return = get_number_to_return()
            return_items = ready_to_return_library_items[0:number_to_return]

            #
            send_email(
                client_secret_file,
                gmail_token_file,
                return_items, gmail_sender
            )
        else:
            pp.pprint(f"failed to get collection_id for {collection_name}")
    else:
        pp.pprint(
            "Please set environment variables COLLECTION_NAME and GMAIL_SENDER")
