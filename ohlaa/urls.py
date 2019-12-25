from django.contrib import admin
admin.autodiscover()
from django.urls import path, include, re_path
from django.views.static import serve
from ohlaa.settings import MEDIA_ROOT
from django.contrib.sitemaps.views import sitemap
from reader.sitemaps import ArticleMap,ChapterMap

sitemaps = {
    'article': ArticleMap,
    'chapter':ChapterMap,
}

urlpatterns = [path('admin/', admin.site.urls),
               re_path(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
                       name='django.contrib.sitemaps.views.sitemap'),
               # path('api/v1/', include('users.urls')),
               path('', include('reader.urls')),
               path('', include('accounts.urls')),
               path('', include('comments.urls')),
               # 富文本编辑器
               path('tinymace/', include('tinymce.urls')),
               # 图形验证码图片路由
               re_path(r'media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
               ]
