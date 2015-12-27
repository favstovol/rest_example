"""rest_example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import patterns, include, url
from django.contrib import admin

from restapp import views

admin.autodiscover()
urlpatterns = patterns('',
url(r'^admin/', include(admin.site.urls)),
url(r'^method/user_get%(?P<st>.+)/$', views.UserGet.as_view()),
url(r'^method/friends_getRequests%(?P<st>.+)/$', views.FriendsGetRequests.as_view()),
url(r'^method/friends_add%(?P<st>.+)/$', views.FriendsAdd.as_view()),
url(r'^method/friends_delete%(?P<st>.+)/$', views.FriendsDelete.as_view()),
url(r'^method/friends_get%(?P<st>.+)/$', views.FriendsGet.as_view()),
url(r'^method/messages_get%(?P<st>.+)/$', views.MessagesGet.as_view()),
url(r'^method/messages_getbyid%(?P<st>.+)/$', views.MessagesGetById.as_view()),
url(r'^method/messages_send%(?P<st>.+)/$', views.MessagesSend.as_view()),
url(r'^method/messages_delete%(?P<st>.+)/$', views.MessagesDelete.as_view()),
url(r'^method/messages_restore%(?P<st>.+)/$', views.MessagesRestore.as_view()),
url(r'^method/messages_getdialogs%(?P<st>.+)/$', views.MessagesGetDialogs.as_view()),
url(r'^method/messages_markasread%(?P<st>.+)/$', views.MessagesMarkAsRead.as_view()),
url(r'^method/messages_gethistory%(?P<st>.+)/$', views.MessagesGetHistory.as_view()),
url(r'', views.HomePage.as_view()),
)