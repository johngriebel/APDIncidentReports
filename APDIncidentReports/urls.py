from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', auth_views.login, {'template_name': "cases/login.html"}, name="login"),
    path('admin/', admin.site.urls),
    path('', include("cases.urls"))
]
