# Lupine: Python Web Framework built for learning purposes

![purpose](https://img.shields.io/badge/purpose-learning-green.svg)

Lupine is a Python web framework built for learning purposes.

It's a WSGI framework and can be used with any WSGI application server such as Gunicorn.


## How to use it

### Basic usage:

```python
from lupine import API

app = API()


@app.route("/")
def home(request, response):
    response.text = "Hello from the home page"


@app.route("/hello/{name}")
def greeting(request, response, name):
    response.text = f"Hello, {name}"


@app.route('/sum/{a:d}/{b:d}')
def hello(request, response, a, b):
    response.text = f'The sum is, {a+b}'


@app.route("/book")
class BooksResource:
    def get(self, request, response):
        response.text = "Books Page"

    def post(self, request, response):
        response.text = "Endpoint to create a book"
    
    def put(self, request, response):
        response.text = "Endpoint to update a book"
    
    def patch(self, request, response):
        response.text = "Endpoint to patch a book"
    
    def delete(self, request, response):
        response.text = "Endpoint to delete a book"


@app.route("/json")
def json_handler(req, resp):
    resp.json = {"name": "data", "type": "JSON"}


@app.route("/template")
def template_handler(req, resp):
    resp.body = app.template(
        "index.html", context={"name": "Lupine", "title": "Best Framework"}).encode()
```

### Unit Tests

The recommended way of writing unit tests is with [pytest](https://docs.pytest.org/en/latest/). There are two built in fixtures
that you may want to use when writing unit tests with Lupine. The first one is `app` which is an instance of the main `API` class:

```python
def test_route_overlap_throws_exception(app):
    @app.route("/")
    def home(req, resp):
        resp.text = "Welcome Home."

    with pytest.raises(AssertionError):
        @app.route("/")
        def home2(req, resp):
            resp.text = "Welcome Home2."
```

The other one is `client` that you can use to send HTTP requests to your handlers. It is based on the famous [requests](http://docs.python-requests.org/en/master/) and it should feel very familiar:

```python
def test_parameterized_route(app, client):
    @app.route("/{name}")
    def hello(req, resp, name):
        resp.text = f"hey {name}"

    assert client.get("http://testserver/matthew").text == "hey matthew"
```

## Templates

The default folder for templates is `templates`. You can change it when initializing the main `API()` class:

```python
app = API(templates_dir="templates_dir_name")
```

Then you can use HTML files in that folder like so in a handler:

```python
@app.route("/show/template")
def handler_with_template(req, resp):
    resp.html = app.template(
        "example.html", context={"title": "Awesome Framework", "body": "welcome to the future!"})
```

## Static Files

Just like templates, the default folder for static files is `static` and you can override it:

```python
app = API(static_dir="static_dir_name")
```

Then you can use the files inside this folder in HTML files:

```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <title>{{title}}</title>

  <link href="/static/main.css" rel="stylesheet" type="text/css">
</head>

<body>
    <h1>{{body}}</h1>
    <p>This is a paragraph</p>
</body>
</html>
```

### Middleware

You can create custom middleware classes by inheriting from the `lupine.middleware.Middleware` class and overriding its two methods
that are called before and after each request:

```python
from api import API
from middleware import Middleware


app = API()


class SimpleCustomMiddleware(Middleware):
    def process_request(self, req):
        print("Before dispatch", req.url)

    def process_response(self, req, res):
        print("After dispatch", req.url)


app.add_middleware(SimpleCustomMiddleware)
```

### Exception handler

You can create custom exception handlers and add them to your project:

```python
from api import API
from middleware import Middleware


app = API()


def custom_exception_handler(request, response, exception_cls):
    response.text = f'Oops, an error has occured, {exception_cls}'

app.add_exception_handler(custom_exception_handler)


@app.route("/exception")
def exception_throwing_handler(request, response):
    raise AssertionError("This handler should not be used.")
```