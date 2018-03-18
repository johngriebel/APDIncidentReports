from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token


urlpatterns = [
    path('login/', auth_views.login, {'template_name': "cases/login.html"}, name="login"),
    path('admin/', admin.site.urls),
    path('', include("cases.urls")),
    path('api-token-auth/', obtain_jwt_token),
    path('api-token-refresh/', refresh_jwt_token),
]

# NOTE: This is for development environments only. Eventually this will be modified for production.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
