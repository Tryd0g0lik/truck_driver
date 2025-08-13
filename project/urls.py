"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from project import settings
from project.urls_api import urlpatterns as api_urls

schema_view = get_schema_view(
    openapi.Info(
        title="DJ Truck Driver API",
        default_version='v1',
        description="DJ Drack API",
        contact=openapi.Contact(email="work80@mail.ru"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path("^person/", include("person.urls", namespace="person")),
    path("api/", include((api_urls, "api_keys"), namespace="api_keys")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger"),
    path(
        "swagger<format>/",
        schema_view.without_ui(cache_timeout=0),
        name="swagger-format",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc"),
    # Person app routes

    # Static and media files
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    re_path(
        r"^(?!static/|media/|api/|admin/|redoc/|swagger/).*",
        TemplateView.as_view(template_name="index.html"),
    ),
]
