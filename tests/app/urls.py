from django.conf.urls import url

from .views import (
    app_view,
    view_with_decorator_with_wraps,
    view_with_decorator_without_wraps
)


url_patterns_with_decorator_with_wraps = [
    url(
        r'^decorator-with-wraps/$', view_with_decorator_with_wraps,
        name='decorator_with_wraps'
    ),
]

# views with custom decorators without @functools.wraps are not supported when specifying app_name
url_patterns_with_decorator_without_wraps = [
    url(
        r'^decorator-without-wraps/$', view_with_decorator_without_wraps,
        name='decorator_without_wraps'
    ),
]

urlpatterns = [
    url(r'^(/(?P<parameter>.+))?', app_view, name='app_view'),
] + url_patterns_with_decorator_with_wraps + url_patterns_with_decorator_without_wraps
