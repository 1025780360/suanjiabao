"""
URL configuration for garment_costing project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.urls import include, path
from django.views.static import serve
from costing.views import CostingChatView

admin.site.site_header = "算价宝后台"
admin.site.site_title = "算价宝后台"
admin.site.index_title = "后台管理"


def health_check(request):
    return JsonResponse({"status": "ok", "service": "garment-costing-api"})


def download_android_apk(request):
    apk_path = settings.BASE_DIR.parent / "frontend" / "public" / "downloads" / "garment-costing.apk"
    if not apk_path.exists():
        raise Http404("APK file not found")
    response = FileResponse(
        apk_path.open("rb"),
        as_attachment=True,
        filename="garment-costing.apk",
        content_type="application/vnd.android.package-archive",
    )
    response["X-Content-Type-Options"] = "nosniff"
    return response


def serve_frontend(request, path=""):
    """生产环境：返回 Vue SPA index.html"""
    import os
    index_path = settings.BASE_DIR / "frontend-dist" / "index.html"
    if not os.path.exists(index_path):
        return HttpResponse("Frontend not built.", status=500)
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
    return HttpResponse(html, content_type="text/html; charset=utf-8")


urlpatterns = [
    path('', serve_frontend, name='index'),
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health-check'),
    path('api/downloads/android-apk/', download_android_apk, name='download-android-apk'),
    path('api/auth/', include('accounts.urls')),
    path('api/costing/', include('costing.urls')),
    path('api/ai/costing-chat/', CostingChatView.as_view(), name='ai-costing-chat'),
    path('assets/<path:path>', serve, {'document_root': settings.BASE_DIR / 'frontend-dist' / 'assets'}),
    path('favicon.svg', serve, {'document_root': settings.BASE_DIR / 'frontend-dist', 'path': 'favicon.svg'}),
    path('app-icon.svg', serve, {'document_root': settings.BASE_DIR / 'frontend-dist', 'path': 'app-icon.svg'}),
    path('manifest.webmanifest', serve, {'document_root': settings.BASE_DIR / 'frontend-dist', 'path': 'manifest.webmanifest'}),
    path('<path:path>', serve_frontend),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
