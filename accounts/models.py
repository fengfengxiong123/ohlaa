from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.urls import reverse
from .utils import get_current_site


# Create your models here.
class OhlaaUser(AbstractUser):
    nickname = models.CharField('昵称', max_length=100, blank=True)
    created_time = models.DateTimeField('创建时间', default=now)
    last_mod_time = models.DateTimeField('修改时间', default=now)
    source = models.CharField('创建来源', max_length=100, blank=True)
    avatar = models.FileField(upload_to='avatar', default='/media/avatars/default.png')

    def get_absolute_url(self):
        return reverse('reader:index', kwargs={'author_name': self.username})

    def __str__(self):
        return self.email

    def get_full_url(self):
        site = get_current_site().domin
        url = 'https://{site}{path}'.format(site=site, path=self.get_absolute_url())
        return url

    class Meta:
        ordering = ['-id']
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        get_latest_by = 'id'
