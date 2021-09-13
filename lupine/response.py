import json

from webob import Response as WebObResponse


class Response:
    def __init__(self):
        self.json = None
        self.html = None
        self.text = None
        self.content_type = None
        self.body = b''
        self.status_code = 200

    def __call__(self, environ, start_response):
        self.set_body_and_content_type()
        
        response = WebObResponse(
            body=self.body,
            content_type=self.content_type,
            status=self.status_code
        )
        return response(environ, start_response)
    
    def set_body_and_content_type(self):
        pass


class TextResponse(Response):
    def set_body_and_content_type(self):
        self.body = self.data
        self.content_type = "text/plain"


class JsonResponse(Response):
    def set_body_and_content_type(self):
        self.body = json.dumps(self.data).encode("UTF-8")
        self.content_type = "application/json"


class HtmlResponse(Response):
    def set_body_and_content_type(self):
        self.body = self.data.encode()
        self.content_type = "text/html"
