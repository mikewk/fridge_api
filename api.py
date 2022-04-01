import quart.flask_patch
import db
import configparser
import logging
import os
import boto3
from quart import Quart, request, jsonify
from ariadne import load_schema_from_path, make_executable_schema, graphql_sync
from ariadne.constants import PLAYGROUND_HTML
from quart import request, jsonify
from sqlalchemy import *
from dotenv import load_dotenv
from quart_cors import cors

load_dotenv(".env")

app = Quart(__name__)
app.debug = true
app = cors(app, allow_origin="*")

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
config.read(os.getenv("SECRET_PATH"))
access_key = config["auth"]["awsid"]
secret_key = config["auth"]["awssecret"]

app.config['SQLALCHEMY_DATABASE_URI'] = mysql_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


def init_graphql():
    from resolvers.mutations import mutations
    from resolvers.queries import queries
    # Setup Resolvers
    type_defs = load_schema_from_path("schema.gql")
    schema = make_executable_schema(
        type_defs, mutations, queries
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
    success, result = graphql_sync(
        graphql_schema,
        data,
        context_value=request,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

graphql_schema = init_graphql()

if __name__ == "__main__":
    app.run(host="192.168.50.130", port=5000, debug=True)
