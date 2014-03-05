from django.conf.urls import patterns, url

from submission import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^login', views.login_user, name='login'),
    url(r'^logout', views.logout_user, name='logout'),
    url(r'^submit', views.submit, name='submit'),
    url(r'^my_results', views.my_results, name='my_results'),
    url(r'^results', views.results, name='results'),
)
