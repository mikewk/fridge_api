import db
import configparser
import logging
import os

from flask import Flask, render_template
from ariadne import load_schema_from_path, make_executable_schema, \
    graphql_sync, snake_case_fallback_resolvers
from ariadne.constants import PLAYGROUND_HTML
from flask import request, jsonify
from sqlalchemy import *
from dotenv import load_dotenv

load_dotenv(".env")

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Setup database
config = configparser.ConfigParser()
config.read(os.getenv("CONFIG_PATH"))
mysql_uri = config["mysql"]["uri"]
app.config['SQLALCHEMY_DATABASE_URI'] = mysql_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

from resolvers.mutations import mutations
from resolvers.queries import queries
# Setup Resolvers
type_defs = load_schema_from_path("schema.gql")
schema = make_executable_schema(
    type_defs, mutations, queries, snake_case_fallback_resolvers
)


# Setup Routes

@app.route("/database")
def database():
    from db import get_db
    d = get_db()
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
def hello_world():
    return {"message": "Hello World...in JSON....FROM FLASK!!"}


@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    global app
    app.logger.info("We are in graphql post")
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code
