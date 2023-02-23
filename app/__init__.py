
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask
from flask_apispec.extension import FlaskApiSpec
from flask_restful import Api

application = Flask(__name__)
application.secret_key = 'flask-restaurant-1234'

api = Api(application)  # Flask restful wraps Flask app around it.

application.config.update({
    'APISPEC_SPEC': APISpec(
        title='Restaurant System Design',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(application)

from app.models import *
