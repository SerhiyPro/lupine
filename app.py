from api import API
from middleware import Middleware


app = API()


@app.route('/home')
def home(request, response):
    response.body = app.template(
        'index.html',
        context={'name': 'Lupine', 'title': 'New framework'}
    ).encode()


@app.route('/about')
def about(request, response):
    response.text = "Hello from the ABOUT page"


@app.route('/hello/{name}')
def hello(request, response, name):
    response.text = f'Hello, {name}'


@app.route('/sum/{a:d}/{b:d}')
def hello(request, response, a, b):
    response.text = f'The sum is, {a+b}'


def handler(req, resp):
    resp.text = "sample"

app.add_route("/sample", handler)


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


def custom_exception_handler(request, response, exception_cls):
    response.text = f'Oops, an error has occured, {exception_cls}'

app.add_exception_handler(custom_exception_handler)


@app.route("/exception")
def exception_throwing_handler(request, response):
    raise AssertionError("This handler should not be used.")


class SimpleCustomMiddleware(Middleware):
    def process_request(self, req):
        print("Processing request", req.url)

    def process_response(self, req, res):
        print("Processing response", req.url)

app.add_middleware(SimpleCustomMiddleware)
