
class VercelPathMiddleware:
    """Restore the original path from Vercel rewrite query parameter."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.GET.get("path")
        if path:
            if not path.startswith("/"):
                path = f"/{path}"
            request.path_info = path
            request.path = path
        return self.get_response(request)