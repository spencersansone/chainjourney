from django.contrib import admin
from django.urls import include
from django.conf.urls import url
from . import views

#These are the urlpatterns that link the page urls to their
#respective views

app_name = 'cryptocurrency'

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login/$', views.login_user, name='login'),
    url(r'^logout/$', views.logout_user, name='logout'),
    url(r'^tracker/$', views.tracker, name='tracker'),
    url(r'^faq/$', views.faq, name='faq'),
    url(r'^journey/$', views.journey, name='journey'),
    url(r'^sources/$', views.sources, name='sources'),
    url(r'^prices/$', views.prices, name='prices'),
    url(r'^payments/$', views.payments, name='payments'),
    url(r'^blog/$', views.blog, name='blog'),
    url(r'^records/$', views.records, name='records'),
    url(r'^userprofile/$', views.userProfile, name='userprofile'),
]
