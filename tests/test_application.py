import pytest

from lupine import API, Middleware


FILE_DIR = "css"
FILE_NAME = "main.css"
FILE_CONTENTS = "body {background-color: red}"

# helpers

def _create_static(static_dir):
    asset = static_dir.mkdir(FILE_DIR).join(FILE_NAME)
    asset.write(FILE_CONTENTS)

    return asset


def test_basic_route_adding(api):
    @api.route("/test-route")
    def check(req, resp):
        resp.text = "hello"


def test_duplicate_route_adding(api):
    @api.route("/test-route")
    def check(req, resp):
        resp.text = "hello"
    
    with pytest.raises(AssertionError):
        @api.route("/test-route")
        def check_duplicate_route(req, resp):
            resp.text = "hello"


def test_client_can_send_requests(api, client):
    RESPONSE_TEXT = "Hello world"

    @api.route("/test")
    def check(req, resp):
        resp.text = RESPONSE_TEXT

    assert client.get("http://testserver/test").text == RESPONSE_TEXT


def test_parameterized_route(api, client):
    @api.route("/{name}")
    def hello(req, resp, name):
        resp.text = f"hello, {name}"

    assert client.get("http://testserver/test").text == "hello, test"
    assert client.get("http://testserver/test1").text == "hello, test1"


def test_default_404_response(client):
    response = client.get("http://testserver/does-not-exist")

    assert response.status_code == 404
    assert response.text == "Not found."


def test_class_based_handler_get(api, client):
    response_text = "This is a test of get request"

    @api.route("/test")
    class TestResource:
        def get(self, req, resp):
            resp.text = response_text

    assert client.get("http://testserver/test").text == response_text


def test_class_based_handler_post(api, client):
    response_text = "This is a test of post request"

    @api.route("/test")
    class TestResource:
        def post(self, req, resp):
            resp.text = response_text

    assert client.post("http://testserver/test").text == response_text


def test_class_based_handler_not_allowed_method(api, client):
    @api.route("/test")
    class TestResource:
        def post(self, req, resp):
            resp.text = "hello world"

    with pytest.raises(AttributeError):
        client.get("http://testserver/test")


def test_alternative_route(api, client):
    response_text = "Alternative way to add a route"

    def home(req, resp):
        resp.text = response_text

    api.add_route("/alternative", home)

    assert client.get("http://testserver/alternative").text == response_text


def test_template_rendering(api, client):
    @api.route("/html")
    def html_handler(req, resp):
        resp.body = api.template("index.html", context={"title": "Some Title", "name": "Some Name"}).encode()

    response = client.get("http://testserver/html")

    assert "text/html" in response.headers["Content-Type"]
    assert "Some Title" in response.text
    assert "Some Name" in response.text


def test_custom_exception_handler(api, client):
    def custom_exception_handler(req, resp, exc):
        resp.text = "AttributeErrorHappened"

    api.add_exception_handler(custom_exception_handler)

    @api.route("/")
    def index(req, resp):
        raise AttributeError()

    response = client.get("http://testserver/")

    assert response.text == "AttributeErrorHappened"


def test_404_is_returned_for_nonexistent_static_file(client):
    assert client.get(f"http://testserver/static/main.css)").status_code == 404


def test_assets_are_served(tmpdir_factory):
    static_dir = tmpdir_factory.mktemp("_static")
    _create_static(static_dir)
    api = API(static_dir=str(static_dir))
    client = api.test_session()

    response = client.get(f"http://testserver/static/{FILE_DIR}/{FILE_NAME}")

    assert response.status_code == 200
    assert response.text == FILE_CONTENTS


def test_middleware_methods_are_called(api, client):
    process_request_called = False
    process_response_called = False

    class CallMiddlewareMethods(Middleware):
        def __init__(self, app):
            super().__init__(app)

        def process_request(self, req):
            nonlocal process_request_called
            process_request_called = True

        def process_response(self, req, resp):
            nonlocal process_response_called
            process_response_called = True

    api.add_middleware(CallMiddlewareMethods)

    @api.route('/')
    def index(req, res):
        res.text = "YOLO"

    client.get('http://testserver/')

    assert process_request_called is True
    assert process_response_called is True


def test_allowed_methods_for_function_based_handlers(api, client):
    response_text = "Just Plain Text"

    @api.route("/home", allowed_methods=["post"])
    def home(req, resp):
        resp.text = response_text

    with pytest.raises(AttributeError):
        client.get("http://testserver/home")

    assert client.post("http://testserver/home").text == response_text

    with pytest.raises(AttributeError):
        client.get("http://testserver/home")


def test_allowed_methods_for_function_based_handlers_alternative_route_adding(api, client):
    response_text = "Just Plain Text"

    def home(req, resp):
        resp.text = response_text

    api.add_route("/home", home, allowed_methods=["post"])
    with pytest.raises(AttributeError):
        client.get("http://testserver/home")

    assert client.post("http://testserver/home").text == response_text

    with pytest.raises(AttributeError):
        client.get("http://testserver/home")


def test_empty_allowed_methods_for_function_based_handlers(api, client):
    @api.route("/home", allowed_methods=[])
    def home(req, resp):
        resp.text = "Shouldn't be accessible"

    with pytest.raises(AttributeError):
        client.get("http://testserver/home")

    with pytest.raises(AttributeError):
        client.post("http://testserver/home")


def test_nullable_allowed_methods_for_function_based_handlers(api, client):
    @api.route("/home", allowed_methods=None)
    def home(req, resp):
        if req.method.lower()  == 'get':
            resp.text = "Hello"
        else:
            resp.text = "World"

    assert client.get("http://testserver/home").text == "Hello"
    assert client.post("http://testserver/home").text == "World"


def test_json_response_helper(api, client):
    @api.route("/json")
    def json_handler(req, resp):
        resp.json = {"name": "bubmo"}

    response = client.get("http://testserver/json")
    json_body = response.json()

    assert response.headers["Content-Type"] == "application/json"
    assert json_body["name"] == "bubmo"


def test_html_response_helper(api, client):
    @api.route("/html")
    def html_handler(req, resp):
        resp.html = api.template("index.html", context={"title": "Best Title", "name": "Best Name"})

    response = client.get("http://testserver/html")

    assert "text/html" in response.headers["Content-Type"]
    assert "Best Title" in response.text
    assert "Best Name" in response.text


def test_text_response_helper(api, client):
    response_text = "Just Plain Text"

    @api.route("/text")
    def text_handler(req, resp):
        resp.text = response_text

    response = client.get("http://testserver/text")

    assert "text/plain" in response.headers["Content-Type"]
    assert response.text == response_text


def test_manually_setting_body(api, client):
    response_text = "Just Plain Text"

    @api.route("/body")
    def text_handler(req, resp):
        resp.body = response_text.encode()
        resp.content_type = "text/plain"

    response = client.get("http://testserver/body")

    assert "text/plain" in response.headers["Content-Type"]
    assert response.text == response_text

