
class InitDynamicTableApiMiddleware(object):
    """
    初始化动态表api中间件
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # # One-time configuration and initialization.

        # from mgmt.initialize import on_ready
        # on_ready()

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
