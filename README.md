# SPARQL helper

This package contains helper functions for SPARQL queries and is made for the [mu.semte.ch](mu.semte.ch) microservice
stack.

Package derived from the [mu-python template](https://github.com/mu-semtech/mu-python-template) helper functions.

### Helper methods

The template provides the user with several helper methods. They aim to give you a step ahead for:

- logging
- JSONAPI-compliancy
- SPARQL querying

The below helpers can be imported from the `helpers` module. For example:

```py
from sparql_helpers.helpers import *
```

Available functions:

#### log(msg)

Works exactly the same as the [logging.info](https://docs.python.org/3/library/logging.html#logging.info) method from
pythons' logging module. Logs are written to the /logs directory in the docker container.  
Note that the `helpers` module also exposes `logger`, which is
the [logger instance](https://docs.python.org/3/library/logging.html#logger-objects) used by the template. The methods
provided by this instance can be used for more fine-grained logging.

#### generate_uuid()

Generate a random UUID (String).

#### session_id_header(request)

Get the session id from the HTTP request headers.

#### rewrite_url_header(request)

Get the rewrite URL from the HTTP request headers.

#### validate_json_api_content_type(request)

Validate whether the Content-Type header contains the JSONAPI `content-type`-header. Returns a 400 otherwise.

#### validate_resource_type(expected_type, data)

Validate whether the type specified in the JSONAPI data is equal to the expected type. Returns a 409 otherwise.

#### error(title, status=400, **kwargs)

Returns a JSONAPI compliant error [Response object](https://flask.palletsprojects.com/en/1.1.x/api/#response-objects)
with the given status code (default: 400). `kwargs` can be any other keys supported
by [JSONAPI error objects](https://jsonapi.org/format/#error-objects).

#### query(query)

Executes the given SPARQL select/ask/construct query.

#### update(query)

Executes the given SPARQL update query.

The template provides one other helper module, being the `escape_helpers`-module. It contains functions for SPARQL
query-escaping. Example import:

```py
from sparql_helpers.escape_helpers import *
```

Available functions:

#### sparql_escape ; sparql_escape_{string|uri|date|datetime|time|bool|int|float}(value)

Converts the given object to a SPARQL-safe RDF object string with the right RDF-datatype.  
This functions should be used especially when inserting user-input to avoid SPARQL-injection.

Separate functions are available for different python datatypes, the `sparql_escape` function however can automatically
select the right method to use, for following Python datatypes:

- `str`
- `int`
- `float`
- `datetime.datetime`
- `datetime.date`
- `datetime.time`
- `boolean`

The `sparql_escape_uri`-function can be used for escaping URI's.