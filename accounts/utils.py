from django.contrib.sites.models import Site
from hashlib import md5
from django.core.cache import cache
import logging
import django.dispatch
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

logger = logging.getLogger(__name__)


def cache_decorator(expiration=3 * 60):
    def wrapper(func):
        def news(*args, **kwargs):
            try:
                view = args[0]
                key = view.get_cache_key()
            except:
                key = None
            if not key:
                unique_str = repr((func, args, kwargs))
                m = md5(unique_str.encode('utf-8'))
                key = m.hexdigest()
            value = cache.get(key)
            if value is not None:
                if str(value) == '__default_cache_value__':
                    return None
                else:
                    return value
            else:
                logger.info('cache_decorator set cache:%s key:%s' % (func.__name__, key))
                value = func(*args, **kwargs)
                if value is None:
                    cache.set(key, '__default_cache_value__', expiration)
                else:
                    cache.set(key, value, expiration)
                return

        return news

    return wrapper


def get_md5(str):
    m = md5(str.encode('utf-8'))
    return m.hexdigest()


@cache_decorator()
def get_current_site():
    site = Site.objects.get_current()
    return site


send_email_signal = django.dispatch.Signal(providing_args=['emailto', 'title', 'content'])


def send_email(emailto, title, content):
    # 事件触发时发送信号
    send_email_signal.send(send_email.__class__, emailto=emailto, title=title, content=content)


@receiver(send_email_signal)
def send_email_signal_handler(sender, **kwargs):
    emailto = kwargs['emailto']
    title = kwargs['title']
    content = kwargs['content']
    msg = EmailMultiAlternatives(title, content, from_email=settings.DEFAULT_FROM_EMAIL, to=emailto)
    msg.content_subtype = 'html'
    from servermanage.models import EmailSendLog
    log = EmailSendLog()
    log.title = title
    log.content = content
    log.emailto = ','.join(emailto)
    try:
        result = msg.send()
        log.send_result = result > 0
    except Exception as e:
        logger.error(e)
        log.send_result = False
    log.save()
