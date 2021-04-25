# from django.contrib.auth.views import logout
from django.urls import path
from . import views


urlpatterns = [
    path('chat/', views.chat_view),
    path('chat/create_group/<group_name>/', views.create_group),
    path('chat/join_group/<group_name>/', views.join_group),
    path('chat/send_message/', views.send_message_to_user_or_group),

]
