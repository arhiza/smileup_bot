from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    url(r'^bot(.*)/$', views.got_message),
    url(r'^quote/(?P<id>[0-9]+)(?:_(?P<code>.*))?/$', views.quote, name="edit_quote"),
]

