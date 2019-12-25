from django.contrib.sitemaps import Sitemap
from .models import Article, ArtChapter
from django.urls import reverse


class ArticleMap(Sitemap):
    changefreq = 'daily'  # 每个对象的更新频率
    priority = 0.6  # 每个对象的优先级,默认0.5

    def items(self):  # 返回对象的列表
        return Article.objects.all().values('id', 'last_mod_time')

    def lastmod(self, obj):  # 表示每个对象的最后修改时间
        return obj['last_mod_time']

    # 如果对象有get_absolute_url()方法,可以省略location
    def location(self, obj):
        return reverse('reader:book', kwargs={'book_id': obj['id']})


class ChapterMap(Sitemap):
    changefreq = 'daily'
    priority = 0.6

    def items(self):
        return ArtChapter.objects.all().values('last_mod_time', 'id', 'article_id')

    def lastmod(self, obj):
        return obj['last_mod_time']

    def location(self, obj):
        return reverse('reader:chapter', kwargs={'book_id': obj['article_id'], 'chapter_id': obj['id']})
