"""
URL configuration for hiringprocess project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from myapp.views import home, login, signup, dashboard, applicants, interviews, selected, rejected, profile, joblisting, reports
from myapp.views import logout_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('dashboard/', dashboard, name='dashboard'),
    path('applicants/', applicants, name='applicants'),
    path('interviews/', interviews, name='interviews'),
    path('selected/', selected, name='selected'),
    path('rejected/', rejected, name='rejected'),
    path('profile/', profile, name='profile'),
    path('reports/',reports, name='reports'),
    path('logout/', logout_view, name='logout'),
    path('joblisting/', joblisting, name='joblisting'),
]
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
