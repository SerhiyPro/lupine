from api import API


app = API()


@app.route('/home')
def home(request, response):
    response.text = "Hello from the HOME page"

@app.route('/about')
def about(request, response):
    response.text = "Hello from the ABOUT page"

@app.route('/hello/{name}')
def hello(request, response, name):
    response.text = f'Hello, {name}'

@app.route('/sum/{a:d}/{b:d}')
def hello(request, response, a, b):
    response.text = f'Hello, {a+b}'


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
