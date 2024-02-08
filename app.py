import os
from flask import Flask
from views import views
from views import flow


app = Flask(__name__)
app.register_blueprint(views,url_prefix="/views")

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.secret_key= flow.client_config.get("client_secret")

if __name__ == '__main__':
    app.run(debug=True,port=8000)