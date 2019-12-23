from django.urls import path,re_path
from . import views

app_name = 'reader'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    re_path(r'store/', views.StoreView.as_view(), name='store'),
    re_path(r'^book/(?P<book_id>[0-9]+)/$', views.BookView.as_view(), name='book'),
    re_path(r'^book/(?P<book_id>[0-9]+)/(?P<chapter_id>[0-9]+)/$', views.ChapterView.as_view(), name='chapter'),
    # path('api/v1/article/', views.ArticleView.as_view(), name='article'),
    # path('api/v1/artchapter/', views.ArtChapterView.as_view(), name='art_chapter'),
    # path('api/v1/chaptercontent/', views.ChapteContentView.as_view(), name='chap_cont'),
    # path('api/v1/hit_rank/', views.HitRankView.as_view(), name='hit_rank'),
    # path('api/v1/hot_rank/', views.HotRankView.as_view(), name='hot_rank'),
    # path('api/v1/category/', views.CategoryView.as_view(), name='category'),
]
