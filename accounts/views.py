from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.generic import FormView, RedirectView
from .forms import RegisterForm, LoginForm
from .utils import get_current_site, get_md5, send_email
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
import logging
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from django.utils.http import is_safe_url

logger = logging.getLogger(__name__)

from django_redis import get_redis_connection

from reader.models import ArtChapter, Article
from accounts.models import HistoryData
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from .models import OhlaaUser


# Create your views here.
class HistoryView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseRedirect('/login/')
        # 连接redis
        con = get_redis_connection('default')
        history_key = 'history_%d' % user.id

        # 获取redis中的历史记录数据 {book_id:chapter_id,}
        history_dict = con.hgetall(history_key)

        art_cha_list = []
        for k, v in history_dict.items():  # 计算进度，将书、章存入列表
            article_obj = Article.objects.get(id=k)
            chapter_obj = ArtChapter.objects.get(id=v)
            # 计算第一章id和最后一章id
            article_first_id = article_obj.artchapter_set.all().first().id
            article_last_id = article_obj.artchapter_set.all().last().id
            # 当计算前章节所占百分比（进度）
            numerator = int(v.decode('utf-8')) - int(article_first_id)
            if numerator == 0:  # 阅读第一章时，分子应该为1
                numerator = 1
            denominator = int(article_last_id) - int(article_first_id)
            progress = '{:.1f}%'.format(numerator / denominator * 100)
            art_cha_list.append({'article': article_obj, 'chapter': chapter_obj, 'progress': progress})
        context = {'art_cha_list': art_cha_list}

        return render(request, 'accounts/history.html', context)


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'accounts/registration_form.html'

    def form_valid(self, form):
        if form.is_valid():
            user = form.save(False)
            user.is_active = False
            user.source = 'Register'
            user.save(True)
            site = get_current_site().domain
            sign = get_md5(get_md5(settings.SECRET_KEY + str(user.id)))
            if settings.DEBUG:
                site = '127.0.0.1:8000'
            path = reverse('accounts:result')
            url = 'http://{site}{path}?type=validation&id={id}&sign={sign}'.format(site=site, path=path, id=user.id,
                                                                                   sign=sign)
            content = """
                                        <p>请点击下面链接验证您的邮箱</p>

                                        <a href="{url}" rel="bookmark">{url}</a>

                                        再次感谢您！
                                        <br />
                                        如果上面链接无法打开，请将此链接复制至浏览器。
                                        {url}
                                        """.format(url=url)
            send_email(emailto=[user.email, ], title='验证您的电子邮箱', content=content)

            url = reverse('accounts:result') + '?type=register&id=' + str(user.id)
            return HttpResponseRedirect(url)
        else:
            return self.render_to_response({
                'form': form
            })


def account_result(request):
    type = request.GET.get('type')
    id = request.GET.get('id')

    user = get_object_or_404(get_user_model(), id=id)
    logger.info(type)
    if user.is_active:
        return HttpResponseRedirect('/')
    if type and type in ['register', 'validation']:
        if type == 'register':
            content = '''
            恭喜您注册成功，一封验证邮件已经发送到您 {email} 的邮箱，请验证您的邮箱后登录本站。
            '''.format(email=user.email)
            title = '注册成功'
        else:
            c_sign = get_md5(get_md5(settings.SECRET_KEY + str(user.id)))
            sign = request.GET.get('sign')
            if sign != c_sign:
                return HttpResponseForbidden()
            user.is_active = True
            user.save()
            content = '''恭喜您已经成功的完成邮箱验证，您现在可以使用您的账号来登录本站。'''
            title = '验证成功'
        return render(request, 'accounts/result.html', {'title': title, 'content': content})
    else:
        return HttpResponseRedirect('/')


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    success_url = '/'
    redirect_field_name = REDIRECT_FIELD_NAME

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):

        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        redirect_to = self.request.GET.get(self.redirect_field_name)
        if redirect_to is None:
            redirect_to = '/'
        kwargs['redirect_to'] = redirect_to
        return super(LoginView, self).get_context_data(**kwargs)

    def form_valid(self, form):

        form = AuthenticationForm(data=self.request.POST, request=self.request)
        if form.is_valid():
            from accounts.utils import cache
            if cache and cache is not None:
                cache.clear()
            logger.info(self.redirect_field_name)
            auth.login(self.request, form.get_user())

            # 登录后获取历史记录存入redis#
            user = self.request.user
            history_key = 'history_%d' % user.id
            con = get_redis_connection('default')
            # <QuerySet [{'book_id': 1, 'chapter_id': 2}, {'book_id': 2, 'chapter_id': 15}]>
            dict_set = HistoryData.objects.filter(history_key=history_key).order_by('-last_mod_time').values(
                'book_id', 'chapter_id')
            for d in dict_set:
                # 从数据库取出历史记录，存入redis
                con.hmset(history_key, {d['book_id']: d['chapter_id']})

            return super(LoginView, self).form_valid(form)

        else:
            return self.render_to_response({'form': form})

    def get_success_url(self):

        redirect_to = self.request.POST.get(self.redirect_field_name)
        if not is_safe_url(url=redirect_to, allowed_hosts=[self.request.get_host()]):
            redirect_to = self.success_url

        return redirect_to


class LogoutView(RedirectView):
    url = '/login/'

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(LogoutView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        from .utils import cache

        cache.clear()  # .clear()删除字典中所有元素
        auth.logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


def upload(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        avatar = request.FILES.get('avatar')
        OhlaaUser.objects.filter(username=name).update(avatar=avatar)
        return HttpResponse('ok')
    return render(request, 'accounts/upload.html')

# def upload(request):
#     if request.method == 'POST':
#         if request.user.is_authenticated:
#             name = request.user.username
#             avatar = request.FILES.get('avatar')
#             OhlaaUser.objects.filter(username=name).update(avatar=avatar)
#             return HttpResponse('ok')
#         return render(request, 'accounts/login.html')
#     return render(request, 'accounts/upload.html')
