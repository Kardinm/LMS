from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from courses.views import HomeView
from courses.downloads import lesson_file, submission_file


urlpatterns = [
    path('media/lesson_materials/<path:filename>', lesson_file, name='lesson_file'),
    path('media/submissions/<path:filename>', submission_file, name='submission_file'),
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('users/', include('users.urls')),
    path('courses/', include('courses.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
