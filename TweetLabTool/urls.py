from django.conf.urls import url, patterns
from Labeller.views import *


urlpatterns = \
    patterns('',
             # Main menu
             url(r'^$', login_view, name="index"),
             # At least 1 character long, can contain hyphens, numbers,
             # underscore and a-z and A-Z
             # Test here: http://www.pyregex.com/
             # url(r'^(?P<username>[-\w]+)/logout/$', logout_view, name="logout"),
             url(r'^(?P<username>.*)/logout/$', logout_view, name="logout"),
             url(r'^register/$', register_view, name="register"),
             # url(r'^labeler/(?P<username>[-\w]+)/annotation/$',
             # Allow any character in URL, specifically @
             url(ur'^labeler/(?P<username>.*)/annotation/$',
                 annotation_view, name="annotation"),
             # url(r'^register/validateUser/$', validate_username),
             url(r'^register/validateEmail/$', validate_email)
   )
