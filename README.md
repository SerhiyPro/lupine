# Lupine: Python Web Framework built for learning purposes

![purpose](https://img.shields.io/badge/purpose-learning-green.svg)

Lupine is a Python web framework built for learning purposes.

It's a WSGI framework and can be used with any WSGI application server such as Gunicorn.


## How to use it

### Basic usage:

```python
from lupine import API
from lupine.response import JsonResponse, Response, TextResponse, HtmlResponse


app = API()


@app.route("/")
def home(request):
    response = TextResponse()
    response.data = "Hello from the home page"
    return response


@app.route("/hello/{name}")
def greeting(request, name):
    response = TextResponse()
    response.data = f"Hello, {name}"
    return response


@app.route('/sum/{a:d}/{b:d}')
def hello(request, a, b):
    response = TextResponse()
    response.data = f'The sum is, {a+b}'
    return response


@app.route("/book")
class BooksResource:
    def get(self, request):
        response = TextResponse()
        response.data = "Books Page"
        return response

    def post(self, request):
        response = TextResponse()
        response.data = "Endpoint to create a book"
        return response
    
    def put(self, request):
        response = TextResponse()
        response.data = "Endpoint to update a book"
        return response
    
    def patch(self, request, response):
        response = TextResponse()
        response.data = "Endpoint to patch a book"
        return response
    
    def delete(self, request, response):
        response = TextResponse()
        response.data = "Endpoint to delete a book"
        return response


@app.route("/json")
def json_handler(request):
    response = JsonResponse()
    response.data = {"name": "data", "type": "JSON"}
    return response


@app.route("/template")
def template_handler(request):
    response = HtmlResponse()
    response.data = app.template(
        "index.html", context={"name": "Lupine", "title": "Best Framework"}
    )
    return response
```

### Unit Tests

The recommended way of writing unit tests is with [pytest](https://docs.pytest.org/en/latest/). There are two built in fixtures
that you may want to use when writing unit tests with Lupine. The first one is `app` which is an instance of the main `API` class:

```python
def test_duplicate_route_adding(api):
    @api.route("/test-route")
    def check(request):
        response = TextResponse()
        response.data = "hello"
        return response
    
    with pytest.raises(AssertionError):
        @api.route("/test-route")
        def check_duplicate_route(request):
            response = TextResponse()
            response.data = "hello"
            return response
```

The other one is `client` that you can use to send HTTP requests to your handlers. It is based on the famous [requests](http://docs.python-requests.org/en/master/) and it should feel very familiar:

```python
def test_parameterized_route(api, client):
    @api.route("/{name}")
    def hello(request, name):
        response = TextResponse()
        response.data = f'hello, {name}'
        return response

    assert client.get("http://testserver/test").text == "hello, test"
    assert client.get("http://testserver/test1").text == "hello, test1"
```

## Templates

The default folder for templates is `templates`. You can change it when initializing the main `API()` class:

```python
app = API(templates_dir="templates_dir_name")
```

Then you can use HTML files in that folder like so in a handler:

```python
@app.route("/template")
def template_handler(request):
    response = HtmlResponse()
    resp.data = app.template(
        "index.html", context={"name": "Lupine", "title": "Best Framework"}
    )
    return response
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
    <p>Test para...</p>
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
    def process_request(self, request):
        print("Before dispatch", request.url)

    def process_response(self, request, response):
        print("After dispatch", request.url)


app.add_middleware(SimpleCustomMiddleware)
```

### Exception handler

You can create custom exception handlers and add them to your project:

```python
from api import API
from middleware import Middleware


app = API()


def custom_exception_handler(request, exc):
        response = TextResponse()
        response.data = "Oops an error has occured"
        return response

app.add_exception_handler(custom_exception_handler)


@app.route("/exception")
def exception_throwing_handler(request):
    raise AssertionError("This handler should not be used.")
```