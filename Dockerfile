FROM python:3.10.2-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# It seems Audible only allow return up to 3 books at a daily basis
ENV NUMBER_TO_RETURN=3
ENV COLLECTION_NAME="Please change to your collection name"
ENV GMAIL_SENDER="Please change to your gmail account"
ENV GMAIL_TOKEN_FILE="Please change to your gmail token file path"
ENV GMAIL_CLIENT_SECRET_FILE="Please change to your gmail client service file path"
ENV AUDIBLE_AUTH_FILE="Please change to your audible auth file path"

COPY . .

CMD [ "python", "./audibot.py" ]