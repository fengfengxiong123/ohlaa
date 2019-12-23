from django.db import models
from accounts.models import OhlaaUser
from tinymce.models import HTMLField  # 富文本
from django.urls import reverse
from django.utils.timezone import now


class Article(models.Model):
    """文章表（表1）"""
    art_name = models.CharField('标题', max_length=200)
    created_time = models.DateTimeField('创建时间', default=now)
    last_mod_time = models.DateTimeField('修改时间', default=now)
    art_author = models.CharField('作者', max_length=10, default="")
    user_owner = models.ForeignKey(OhlaaUser, on_delete=models.CASCADE)
    type_choices = [
        ('流行', (
            ('xuanhuan', '玄幻'),
            ('qihuan', '奇幻'),
            ('kehuan', '科幻'),
            ('wuxia', '武侠'),
            ('xianxia', '仙侠'),
            ('dushi', '都市'),
            ('yanqing', '言情'),
            ('lishi', '历史'),
        )),
        ('经典', (
            ('mingzhu', '名著'),
            ('shenhua', '神话'),
            ('xiaoshuo', '小说'),
            ('zhuzi', '诸子'),
            ('shici', '诗词'),
            ('shishu', '史书'),
        ))
    ]
    art_type = models.CharField(max_length=200, choices=type_choices)
    art_status = models.CharField('状态', max_length=200, default="")
    art_introduction = models.CharField('简介', max_length=2000, default="")
    art_name_used = models.CharField('曾用名', max_length=200, default="")
    art_hits = models.IntegerField('点击量', default='0')
    art_hots = models.IntegerField('点击量', default='0')
    word_number = models.IntegerField(verbose_name='字数', default=0, null=True)
    comment_nums = models.IntegerField(verbose_name='评论数', default=0, null=True)

    class Meta:
        ordering = ['created_time']

    def __str__(self):
        if len(self.art_name) >= 20:
            art_name_limit = self.art_name[:20] + '...'
        else:
            art_name_limit = self.art_name
        # 限制返回文章名字符数
        return art_name_limit

    def get_absolute_url(self):
        return reverse('reader:book', kwargs={
            'book_id': self.id,
            # 'year': self.created_time.year,
            # 'month': self.created_time.month,
            # 'day': self.created_time.day,
        })


class ArtChapter(models.Model):
    """文章章节内容表(表2）"""
    chapter_name = models.CharField('章名', max_length=200)
    chapter_content = HTMLField('文章内容')
    article = models.ForeignKey(Article, verbose_name="文章", on_delete=models.CASCADE, null=True)
    chapter_add_date = models.DateTimeField(auto_now=True)
    word_number = models.IntegerField(verbose_name='字数', default=0, null=True)
    chapter_hits = models.IntegerField(verbose_name='点击', default='0', null=True)
    chapter_hots = models.IntegerField(verbose_name='推荐', default='0', null=True)

    class Meta:
        ordering = ['id']
