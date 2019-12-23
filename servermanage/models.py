from django.db import models


# Create your models here.
class EmailSendLog(models.Model):
    emailto = models.CharField('收件人', max_length=300)
    title = models.CharField('邮件标题', max_length=2000)
    content = models.TextField('邮件内容')
    send_result = models.BooleanField('结果', default=False)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '邮件发送日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_time']
