from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('spotifyarchiveapp.urls')),
    path('admin/', admin.site.urls),
]

handler404 = 'spotifyarchiveapp.views.page_not_found'
handler500 = 'spotifyarchiveapp.views.error'
#handler403 = 'spotifyarchiveapp.views.permission_denied'
#handler400 = 'spotifyarchiveapp.views.bad_request'