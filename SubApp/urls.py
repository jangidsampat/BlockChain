from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home),
    path('home/', views.home, name='home'),
    path('viewBlock/', views.viewBlock, name='viewBlock'),
    path('viewUser/', views.viewUser, name='viewUser'),
    path('addBlock/', views.addBlock, name='addBlock'),
    path('addNewBlock/', views.addNewBlock, name='addNewBlock'),
    path('updateBlock/', views.updateBlock, name='updateBlock'),
    path('transferBlock/', views.transferBlock, name='transferBlock'),
    path('signup/', views.signup, name='signup'),
    path('signUpUser/', views.signUpUser, name='signUpUser'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login, name='login'),
    path('loginUser/', views.loginUser, name='loginUser'),
    path('logout/', views.logout, name='logout'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
