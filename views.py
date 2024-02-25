import os
import pathlib
import random
import sys
import time
import generate

import google.auth.transport.requests
import httplib2
import requests
from flask import Blueprint, render_template, abort, redirect, url_for, request, session
from google.oauth2 import id_token
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import AccessTokenCredentials, Storage, flow_from_clientsecrets
from oauth2client.tools import run_flow
from pip._vendor import cachecontrol

views = Blueprint(__name__, "views", static_folder="static", template_folder="templates")
request_session = requests.Session()

Google_Client_ID = "926083527735-ste8ur2scs0li21ajl5thfq8j0hcpufr.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
flow = InstalledAppFlow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email",
            "openid", "https://www.googleapis.com/auth/youtube.upload"],
    redirect_uri="http://127.0.0.1:8000/views/callback")

# flow.run_local_server(port=8080, prompt="consent")
# credentials = flow.credentials
# print(credentials)
# youtube = build("youtube", "v3",credentials=credentials)
httplib2.RETRIES = 1

MAX_RETRIES = 10

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def initialize_upload(youtube, options):
    tags = None
    if options['keywords']:
        tags = options['keywords'].split(",")

    body = dict(
        snippet=dict(
            title=options['title'],
            description=options['description'],
            tags=tags,
            categoryId=options['categoryId']
        ),
        status=dict(
            privacyStatus=options['privacyStatus']
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options['filename'], chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)


def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print("Video id '%s' was successfully uploaded." % response['id'])
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                     e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)


@views.route("/tryuploadToYT")
def upload_videoTest123():
    options = {
        "filename": "VID-20230922-WA0029.mp4",
        "title": "Example title",  # The video title
        "description": "Example description",  # The video description
        "keywords": "shorts, curiosity",
        "categoryId": "22",
        "privacyStatus": "private",  # Video privacy. Can either be "public", "private", or "unlisted"
    }
    flow2 = flow_from_clientsecrets(os.path.join(pathlib.Path(__file__).parent, "client_secret.json"),
                                    scope="https://www.googleapis.com/auth/youtube.upload")

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow2, storage, options)

    credentials = build("youtube", "v3", credentials=credentials)

    try:
        initialize_upload(credentials, options)
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return redirect(url_for("views.login"))  # abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@views.route("/")
def home():
    return render_template("default_scr.html")


@views.route("/uploadmedia")
@login_is_required
def upload():
    return render_template("uploadMedia_scr.html")


@views.route("/uploadmedia/<filename>", methods=['POST'])
def getuploadedSelectedAspect(filename, aspect):
    generate.generate_title_aspect_suggestions(filename)
    return render_template("uploadMedia_scr.html", file=filename, aspect=aspect)


@views.route("/selectitems")
def select():
    args = request.args
    filename = args.get('filename')
    aspect = args.get('aspect')
    return render_template("select_scr.html")


@views.route("/uploadToYT")
def uploadToYT():
    return render_template("uploadToYT_scr.html")


@views.route("/personal")
def personal():
    return render_template("personal_scr.html")


@views.route("/home")
def mainhome():
    return render_template("home_scr.html")


@views.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


def get_authenticated_service():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        request=token_request,
        audience=None,  # flow.client_config.get("client_id"),
        id_token=credentials._id_token
    )

    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes}
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    session["token"] = credentials.token
    session["state"] = request.args["state"]
    session["refresh_token"] = credentials.refresh_token
    session["token_uri"] = credentials.token_uri
    session["client_id"] = credentials.client_id
    session["client_secret"] = credentials.client_secret

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = AccessTokenCredentials(session["token"], session["refresh_token"], session["token_uri"])
    return credentials


@views.route("/callback")
def callback():
    get_authenticated_service()
    return redirect(url_for("views.wrapper"))


@views.route("/logout")
def logout():
    session.pop("user", None)
    session.clear()
    requests.post('https://oauth2.googleapis.com/revoke',
                  params={'token': id_token},
                  headers={'content-type': 'application/x-www-form-urlencoded'})
    return redirect(url_for("views.home"))


@views.route("/protected_area")
# @login_is_required
def protected_area():
    return render_template("main.html", name=session['name'])
