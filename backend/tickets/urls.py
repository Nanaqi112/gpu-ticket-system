from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, login_view, logout_view, user_info

router = DefaultRouter()
router.register(r'tickets', TicketViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/user/', user_info, name='user-info'),
]