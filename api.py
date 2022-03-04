from flask import Flask, render_template
import db
import configparser
import logging
from sqlalchemy import *
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
#Setup database

config = configparser.ConfigParser()
config.read('/var/www/config.ini')
mysql_uri= config["mysql"]["uri"]
app.config['SQLALCHEMY_DATABASE_URI'] = mysql_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route("/database")
def database():
    from db import get_db

    d = get_db()
    d.create_all()
    m = MetaData(d.engine)
    m.reflect()
    result = {}
    for table in m.sorted_tables:
        result[table.name] = {}
        for column in table.c:
            result[table.name][column.name] = type(column.type).__name__
    return result

@app.route("/")
def hello_world():
    return {"message":"Hello World...in JSON....FROM FLASK!!"}


from ariadne import load_schema_from_path, make_executable_schema, \
    graphql_sync, snake_case_fallback_resolvers, ObjectType
from ariadne.constants import PLAYGROUND_HTML
from flask import request, jsonify
from resolvers.mutations import mutations
from resolvers.queries import queries

type_defs = load_schema_from_path("/var/www/fridge/api/schema.gql")
schema = make_executable_schema(
    type_defs, mutations, queries, snake_case_fallback_resolvers
)

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