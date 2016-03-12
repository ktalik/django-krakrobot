from django.conf import settings
from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.contrib import admin

import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login', views.login_user, name='login'),
    url(r'^logout', views.logout_user, name='logout'),
    url(r'^old_submit', views.submit, name='submit'),
    url(r'^submit', views.submit, name='submit'),
    url(r'^my_results', views.my_results, name='my_results'),
    url(r'^results', views.results, name='results'),
    url(r'^admin', include(admin.site.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
