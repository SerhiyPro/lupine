import pytest


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


def test_bumbo_test_client_can_send_requests(api, client):
    RESPONSE_TEXT = "Hello world"

    @api.route("/test")
    def cool(req, resp):
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
    class BookResource:
        def get(self, req, resp):
            resp.text = response_text

    assert client.get("http://testserver/test").text == response_text


def test_class_based_handler_post(api, client):
    response_text = "This is a test of post request"

    @api.route("/test")
    class BookResource:
        def post(self, req, resp):
            resp.text = response_text

    assert client.post("http://testserver/test").text == response_text


def test_class_based_handler_not_allowed_method(api, client):
    @api.route("/test")
    class BookResource:
        def post(self, req, resp):
            resp.text = "hello world"

    with pytest.raises(AttributeError):
        client.get("http://testserver/test")
