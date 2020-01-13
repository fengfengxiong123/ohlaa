from django.contrib import admin

admin.autodiscover()
from django.urls import path, include, re_path
from django.views.static import serve
from ohlaa.settings import MEDIA_ROOT
from django.contrib.sitemaps.views import sitemap
from reader.sitemaps import ArticleMap, ChapterMap
from django.views.generic import TemplateView

sitemaps = {
    'article': ArticleMap,
    'chapter': ChapterMap,
}

urlpatterns = [path('admin/', admin.site.urls),

               # 生产环境中，通过收集命令将文件收集到/data/ohlaa/static，
               # nginx 服务器获取静态文件 /sitemap.xml  /robots.txt,
               path('', include('reader.urls')),
               path('', include('accounts.urls')),
               path('', include('comments.urls')),
               # 富文本编辑器
               path('tinymace/', include('tinymce.urls')),
               # 图形验证码图片路由
               re_path(r'media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
               re_path(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
                       name='django.contrib.sitemaps.views.sitemap'),# 生成sitemap的url
               ]
