from django.views.generic.edit import FormView
from .forms import CommentForm
from reader.models import Article
from django.http import HttpResponseRedirect
from django import forms
from django.contrib.auth import get_user_model
from .models import Comment
from django.shortcuts import render


# Create your views here.
class CommentPostView(FormView):
    form_class = CommentForm
    template_name = 'reader/book.html'

    def get(self, request, *args, **kwargs):
        print(self.kwargs)
        book_id = self.kwargs['book_id']
        article = Article.objects.get(pk=book_id)

        url = article.get_absolute_url()

        return HttpResponseRedirect(url + '#comments')

    def form_invalid(self, form):
        print('不合法')
        book_id = self.kwargs['book_id']
        article = Article.objects.get(pk=book_id)

        if self.request.user.is_authenticated:
            form.fields.update({
                'email': forms.CharField(widget=forms.HiddenInput()),
                'name': forms.CharField(widget=forms.HiddenInput()),
            })
            user = self.request.user
            form.fields['email'].initial = user.email
            form.fields['name'].initial = user.username
        return self.render_to_response({
            'form': form,
            'article': article
        })

    def form_valid(self, form):
        """提交的数据验证合法后的逻辑"""

        user = self.request.user
        book_id = self.kwargs['book_id']
        article = Article.objects.get(pk=book_id)
        if not self.request.user.is_authenticated:
            return render(self.request,'accounts/login.html')
            # email = form.cleaned_data['email'] # 如匿名用户，使用邮箱和用户名创建用户！！！！
            # username = form.cleaned_data['name']
            # user = get_user_model().objects.get_or_create(username=username, email=email, is_active=0)[0]
        comment = form.save(False)
        comment.article = article
        comment.author = user
        if form.cleaned_data['parent_comment_id']:
            parent_comment = Comment.objects.get(pk=form.cleaned_data['parent_comment_id'])
            comment.parent_comment = parent_comment
        comment.save(True)
        return HttpResponseRedirect(
            '%s#div-comment-%d' % (article.get_absolute_url(), comment.pk))  # 锚点到id=div-commen-x的元素
