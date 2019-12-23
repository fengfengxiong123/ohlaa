from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from ohlaa.settings import MEDIA_ROOT

urlpatterns = [path('admin/', admin.site.urls),
               # path('api/v1/', include('users.urls')),
               path('', include('reader.urls')),
               path('', include('accounts.urls')),
               path('', include('comments.urls')),
               # 富文本编辑器
               path('tinymace/', include('tinymce.urls')),
               # 图形验证码图片路由
               re_path(r'media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
               ]
