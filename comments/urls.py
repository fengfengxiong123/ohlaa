from django.urls import re_path
from . import views

app_name = 'comments'
urlpatterns = [
    re_path(r'^book/(?P<book_id>[0-9]+)/postcomment/$', views.CommentPostView.as_view(), name='postcomment'),
]
