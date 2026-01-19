from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.deprecation import MiddlewareMixin

from .backends import H34vvySessionStore, is_h34vvy_u53rzz_request


class H34vvySessionMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        # SessionMiddleware.process_response はインスタンス引数
        # self を一度も触っていないので、そのまま流用する
        self.process_response_impl = SessionMiddleware(get_response).process_response

    def process_request(self, request):
        if is_h34vvy_u53rzz_request(request):
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
            request.session = H34vvySessionStore(session_key)

    def process_response(self, request, response):
        if is_h34vvy_u53rzz_request(request):
            return self.process_response_impl(request, response)
        return response
