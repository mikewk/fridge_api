import quart.flask_patch
import asyncio
from django.urls import path, re_path

import db
import configparser
import logging
import os

from ariadne import load_schema_from_path, make_executable_schema, graphql_sync, graphql
from ariadne.asgi import GraphQL
from ariadne.constants import PLAYGROUND_HTML
from quart import Quart, request, jsonify
from sqlalchemy import *
from dotenv import load_dotenv
from quart_cors import cors
from channels.routing import URLRouter
from hypercorn.config import Config
from hypercorn.asyncio import serve

load_dotenv(".env")

app = Quart(__name__)
app = cors(app, allow_origin="*")
app.debug = true

logging.basicConfig(level=logging.DEBUG)

# setup S3 logging levels
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('nose').setLevel(logging.WARNING)
logging.getLogger('s3transfer').setLevel(logging.WARNING)


# Setup database
config = configparser.ConfigParser()
config.read(os.getenv("CONFIG_PATH"))
mysql_uri = config["mysql"]["uri"]
upload_base = config["directories"]["upload"]
bind_address = config["bind"]["address"]
config.read(os.getenv("SECRET_PATH"))
access_key = config["auth"]["awsid"]
secret_key = config["auth"]["awssecret"]

app.config['SQLALCHEMY_DATABASE_URI'] = mysql_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


def init_graphql():
    from resolvers.mutations import mutations
    from resolvers.queries import queries
    from resolvers.subscriptions import subscriptions
    # Setup Resolvers
    type_defs = load_schema_from_path("schema.gql")
    schema = make_executable_schema(
        type_defs, mutations, queries, subscriptions
    )
    return schema


# Setup Routes
@app.route("/database")
async def database():
    from db import get_db
    d = get_db()
    d.create_all()
    d.session.commit()
    m = MetaData(d.engine)
    m.reflect()
    result = {}
    for table in m.sorted_tables:
        result[table.name] = {}
        for column in table.c:
            result[table.name][column.name] = type(column.type).__name__
    return result


# Add comment to test repo
@app.route("/")
async def hello_world():
    return {"message": "Hello World...in JSON....FROM FLASK!!"}


@app.route("/graphql", methods=["GET"])
async def graphql_playground():
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
async def graphql_server():
    global app
    data = await request.get_json()
    success, result = await graphql(
        graphql_schema,
        data,
        context_value=request,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code


graphql_schema = init_graphql()
asgiHandler = GraphQL(graphql_schema, debug=True)

application = URLRouter([
    path("ws", asgiHandler),
    re_path(r"", app)
    ]
)

if __name__ == "__main__":
    config = Config()
    config.bind = bind_address
    asyncio.run(serve(application, config))

try:
    loop = asyncio.get_running_loop()
except RuntimeError as e:
    print("Couldn't get loop")
    exit(1)
