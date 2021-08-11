import uuid
import datetime
import logging
import os
import sys
from flask import jsonify, request
from rdflib.namespace import DC
from .escape_helpers import sparql_escape
from SPARQLWrapper import SPARQLWrapper, JSON

MU_APPLICATION_GRAPH = os.environ.get('MU_APPLICATION_GRAPH')

# TODO: Figure out how logging works when production uses multiple workers
log_levels = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}
log_dir = '/logs'
if not os.path.exists(log_dir): os.makedirs(log_dir)
logger = logging.getLogger('MU_PYTHON_TEMPLATE_LOGGER')
logger.setLevel(log_levels.get(os.environ.get('LOG_LEVEL').upper()))
fileHandler = logging.FileHandler("{0}/{1}.log".format(log_dir, 'logs'))
logger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler(stream=sys.stdout)  # or stderr?
logger.addHandler(consoleHandler)


def generate_uuid():
    """
    Generates a unique user id based the host ID and current time
    :return: string:uuid
    """
    return str(uuid.uuid1())


def log(msg, *args, **kwargs):
    """
    write a log message to the log file. Logs are written to the `/logs` directory in the docker container.
    :param msg: log message
    :param args: args
    :param kwargs: kwargs
    :return: logger info message
    """
    return logger.info(msg, *args, **kwargs)


def session_id_header(request):
    """
    Returns the MU-SESSION-ID header from the given request.
    Only valid when called after receiving a flask request.
    :param request: flask http request
    :return: string:request MU-SESSION-ID header
    """
    return request.headers.get('MU-SESSION-ID')


def rewrite_url_header(request):
    """
    Return the X-REWRITE-URL header from the given request.
    Only valid when called after receiving a flask request.
    :param request: flask http request
    :return: string:request X-REWRITE-URL header
    """
    return request.headers.get('X-REWRITE-URL')


def error(msg, status=400, **kwargs):
    """
    Returns a Response object containing a JSONAPI compliant error response with the given status code (400 by default).
    :param msg: error message
    :param status: status number
    :param kwargs: kwargs
    :return: response message
    """
    error_obj = kwargs
    error_obj["detail"] = msg
    error_obj["status"] = status
    response = jsonify({
        "errors": [error_obj]
    })
    response.status_code = error_obj["status"]
    response.headers["Content-Type"] = "application/vnd.api+json"
    return response


def validate_json_api_content_type(request):
    """
    Validate whether the content type of the request is application/vnd.api+json.
    Only valid when called after receiving a flask request.
    :param request: flask http request
    :return
    """
    if "/^application/vnd.api+json" not in request.args.get('CONTENT_TYPE'):
        return error("Content-Type must be application/vnd.api+json instead of" +
                     request.args.get('CONTENT_TYPE'))


def validate_resource_type(expected_type, data):
    """
    Validate whether the type specified in the JSON data is equal to the expected type.
    Returns a `409` otherwise.
    :param expected_type: expected datatype to verify
    :param data: json data
    :return: 409 if JSON data is equal to expected type
    """
    if data['type'] is not expected_type:
        return error("Incorrect type. Type must be " + str(expected_type) +
                     ", instead of " + str(data['type']) + ".", 409)


sparqlQuery = SPARQLWrapper(os.environ.get('MU_SPARQL_ENDPOINT'), returnFormat=JSON)
sparqlUpdate = SPARQLWrapper(os.environ.get('MU_SPARQL_UPDATEPOINT'), returnFormat=JSON)
sparqlUpdate.method = 'POST'
if os.environ.get('MU_SPARQL_TIMEOUT'):
    timeout = int(os.environ.get('MU_SPARQL_TIMEOUT'))
    sparqlQuery.setTimeout(timeout)
    sparqlUpdate.setTimeout(timeout)

MU_HEADERS = [
    "MU-SESSION-ID",
    "MU-CALL-ID",
    "MU-AUTH-ALLOWED-GROUPS",
    "MU-AUTH-USED-GROUPS"
]


def query(the_query):
    """
    Execute the given SPARQL query (select/ask/construct)on the tripple store and returns the results
    in the given returnFormat (JSON by default).
    :param the_query: SPARQL query
    :return: json:query response
    """
    log("execute query: \n" + the_query)
    if request:
        for header in MU_HEADERS:
            if header in request.headers:
                sparqlQuery.customHttpHeaders[header] = request.headers[header]
            else:  # Make sure headers used for a previous query are cleared
                if header in sparqlQuery.customHttpHeaders:
                    del sparqlQuery.customHttpHeaders[header]
    sparqlQuery.setQuery(the_query)
    return sparqlQuery.query().convert()


def update(the_query):
    """
    Execute the given update SPARQL query on the tripple store,
    if the given query is no update query, nothing happens.
    :param the_query: SPARQL query
    :return: json:query response
    """
    if request:
        for header in MU_HEADERS:
            if header in request.headers:
                sparqlUpdate.customHttpHeaders[header] = request.headers[header]
            else:  # Make sure headers used for a previous query are cleared
                if header in sparqlUpdate.customHttpHeaders:
                    del sparqlUpdate.customHttpHeaders[header]
    sparqlUpdate.setQuery(the_query)
    if sparqlUpdate.isSparqlUpdateRequest():
        sparqlUpdate.query()


def update_modified(subject, modified=datetime.datetime.now()):
    """
    Executes a SPARQL query to update the modification date of the given subject URI (string).
    :param subject: subject of triple
    :param modified: modification time
    :return: json:update query response
    """
    query = " WITH <%s> " % MU_APPLICATION_GRAPH
    query += " DELETE {"
    query += "   < %s > < %s > %s ." % (subject, DC.Modified, sparql_escape(modified))
    query += " }"
    query += " WHERE {"
    query += "   <%s> <%s> %s ." % (subject, DC.Modified, sparql_escape(modified))
    query += " }"
    update(query)

    query = " INSERT DATA {"
    query += "   GRAPH <%s> {" % MU_APPLICATION_GRAPH
    query += "     <%s> <%s> %s ." % (subject, DC.Modified, sparql_escape(modified))
    query += "   }"
    query += " }"
    update(query)
