import inspect

from parse import parse
from webob import Request, Response
from requests import Session as RequestSession
from wsgiadapter import WSGIAdapter as RequestWSGIAdapter


class API:
    def __init__(self) -> None:
        self.routes = {}
    
    def __call__(self, environ, start_response):
        request = Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)
    
    def add_route(self, path, handler):
        assert path not in self.routes, "Such route already exists."
        
        self.routes[path] = handler

    def route(self, path):
        def wrapper(handler):
            self.add_route(path, handler)
            return handler
        return wrapper
    
    def default_response(self, response):
        response.status_code = 404
        response.text = "Not found."
    
    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            parsed_result = parse(path, request_path)
            if parsed_result is not None:
                return handler, parsed_result.named
        return None, None

    def handle_request(self, request):
        response = Response()

        handler, kwargs = self.find_handler(request_path=request.path)

        if handler is not None:
            if inspect.isclass(handler):
                handler = getattr(handler(), request.method.lower(), None)
                if handler is None:
                    raise AttributeError("Method not allowed", request.method)

            handler(request, response, **kwargs)
        else:
            self.default_response(response)

        return response
    
    def test_session(self, base_url="http://testserver"):
        session = RequestSession()
        session.mount(prefix=base_url, adapter=RequestWSGIAdapter(self))
        return session
