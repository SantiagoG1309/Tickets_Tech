from threading import local

_thread_locals = local()

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Almacenar el usuario actual en el contexto local
        _thread_locals.user = getattr(request, 'user', None)
        response = self.get_response(request)
        return response