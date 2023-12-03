FROM python:3.10.2-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# It seems Audible only allow return up to 3 books at a daily basis
ENV NUMBER_TO_RETURN=6
ENV COLLECTION_NAME="Ready for return"
ENV GMAIL_SENDER="Please put you email address here"
ENV GMAIL_TOKEN_FILE="/config/gmail_token.json"
ENV GMAIL_CLIENT_SECRET_FILE="/config/client_secret.json"
ENV AUDIBLE_AUTH_FILE="/config/audible_auth.json"

COPY . .

CMD [ "python", "./audibot.py" ]