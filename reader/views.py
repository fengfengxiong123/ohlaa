from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
# from rest_framework.response import Response
from .models import Article, ArtChapter
from comments.models import Comment
from .pagination import MyPageNumberPagination
from .serializer import ArticleSerializer
import json
from accounts.models import OhlaaUser


# Create your views here.
class IndexView(APIView):
    """主页：点击、热度排行"""

    def get(self, request):
        art_obj_hits = Article.objects.all().order_by('-art_hits')[0:10]
        art_obj_hots = Article.objects.all().order_by('-art_hots')[0:10]
        art_obj_comm_num = Article.objects.all().order_by('-comment_nums')[0:5]

        arts_nums = []
        for obj in art_obj_comm_num:
            comment_objs = Comment.objects.all().filter(article_id=obj.id)[0:2]
            arts_nums.append({'obj': obj, 'comments': comment_objs})

        context = {'hits': art_obj_hits, 'hots': art_obj_hots, 'arts_nums': arts_nums}

        return render(request, 'reader/index.html', context)


class StoreView(APIView):
    """书库：简介去首尾空格"""

    def get(self, request, *args, **kwargs):
        articles = Article.objects.all().values('art_name', 'created_time', 'art_author', 'art_type', 'art_status',
                                                'art_introduction', 'art_hits', 'id')
        context = {'articles': articles}
        return render(request, 'reader/store.html', context)


from comments.forms import CommentForm


class BookView(APIView):
    """书籍列表"""

    def get(self, request, *args, **kwargs):

        book_id = kwargs['book_id']

        form = CommentForm()

        article = Article.objects.filter(id=book_id)[0]
        chapters = ArtChapter.objects.filter(article_id=book_id)
        num = 0
        hits_num = 0
        for chapter in chapters:  # 所有章节字数相加存入数据库
            if not chapter.word_number:
                chapter.word_number = 0
            num = num + chapter.word_number  # 所有章节字数相加
            article.word_number = num
            if not chapter.chapter_hits:
                chapter.chapter_hits = 0
            hits_num = hits_num + chapter.chapter_hits  # 所有章节点击量相加
            article.art_hits = hits_num

        article.save()
        last_chap = chapters.last()  # 最后更新章节
        chapter_num = len(chapters)

        comment_list = list(
            Comment.objects.all().filter(article_id=book_id).values('id', 'body', 'parent_comment_id', 'author_id'))
        for comment in comment_list:  #
            comment['author'] = OhlaaUser.objects.get(id=comment['author_id'])  # 遍历列表，为每个字典添加作者

        comment_dict = {}
        for comment in comment_list:
            comment['children_comment'] = []  # 每个评论添加 '子评论':[]
            comment_dict[comment['id']] = comment  # 评论字典添加 key=评论id ，value=评论字典本身

        # 获得类似这样{1: {'id': 1, 'body': '评论1', 'parent_comment_id': None,
        # 'author_id': 1, 'author': <OhlaaUser: 359975715@qq.com>, 'children_comment': []},}的字典

        comment_tree = []

        for comment in comment_list:

            pid = comment['parent_comment_id']

            if pid:  # 如果有父评论
                comment_dict[pid]['children_comment'].append(comment)
            else:  # 如果没有父评论
                comment_tree.append(comment)

        context = {'form': form, 'article': article, 'chapters': chapters, 'chapter_num': chapter_num,
                   'last_chap': last_chap, 'comment_tree': comment_tree}

        return render(request, 'reader/book.html', context)


from django.views.decorators.cache import cache_control


class ChapterView(APIView):

    @cache_control(must_revalidate=True, max_age=60)
    def get(self, request, **kwargs):
        book_id = kwargs['book_id']
        chapter_id = kwargs['chapter_id']
        article = \
            Article.objects.filter(id=book_id).values('id', 'art_name', 'art_type', 'art_introduction', 'art_author')[0]
        chapter = ArtChapter.objects.filter(article_id=book_id, id=chapter_id)[0]
        if chapter.chapter_hits:
            chapter.chapter_hits += 1  # 章点击量+1
        else:
            chapter.chapter_hits = 1
        if not chapter.word_number:
            num = 0
            for word in chapter.chapter_content:
                if '\u4e00' <= word <= '\u9fff':
                    num += 1

            chapter.word_number = num

        chapter.save()

        previous = ArtChapter.objects.filter(article_id=book_id, id__lt=chapter_id).order_by('-id').first()  # __gt 小于
        next_article = ArtChapter.objects.filter(article_id=book_id, id__gt=chapter_id).order_by('id').first()
        context = {'article': article, 'chapter': chapter, 'previous': previous, 'next': next_article}
        return render(request, 'reader/chapter.html', context)


class ArticleView(APIView):
    authentication_classes = []

    def get(self, request):
        """
        示例： /api/v1/article/？pageNum=1&pageSize=3
        """
        # page_id = request.query_params.dict().get('pageNum')
        search_name = request.GET.get('search_name')
        page_num = request.GET.get('pageNum')
        page_size = request.GET.get('pageSize')
        ca = request.GET.get('ca')
        if page_num or page_size:
            article = Article.objects.all()
            pg = MyPageNumberPagination()  # 自定义分页对象
            pager_articles = pg.paginate_queryset(queryset=article, request=request, view=self)
            ser = ArticleSerializer(instance=pager_articles, many=True)
            data = []
            for i in ser.data:
                i['art_introduction'] = i['art_introduction'].strip()
                data.append(i)
            ret = {'code': 1000, 'msg': None, 'lens': None, 'data': None}
            try:
                ret['msg'] = '成功'
                ret['data'] = data
                ret['lens'] = len(data)
            except Exception as e:
                ret['code'] = 1001
                ret['msg'] = '失败'
                print(e)
            # return pg.get_paginated_response(ret)


        elif search_name:
            if not search_name:
                error_msg = '请输入关键词'
                print(type(error_msg))
                print(type(json.dumps(error_msg)))
                return HttpResponse(error_msg)
            articles = Article.objects.filter(art_name__icontains=search_name)
            ser = ArticleSerializer(instance=articles, many=True)
            ret = {'code': 1000, 'msg': None, 'lens': None, 'data': None}
            try:
                ret['msg'] = '成功'
                ret['data'] = ser.data
                ret['lens'] = len(articles)
            except Exception as e:
                ret['code'] = 1001
                ret['msg'] = '失败'
                print(e)
            # return pg.get_paginated_response(ret)

        elif ca:
            articles = Article.objects.all().filter(art_type=ca)
            ser = ArticleSerializer(instance=articles, many=True)
            ret = {'code': 1000, 'msg': None, 'lens': None, 'data': None}
            try:
                ret['msg'] = '成功'
                ret['data'] = ser.data
                ret['lens'] = len(articles)
            except Exception as e:
                ret['code'] = 1001
                ret['msg'] = '失败'
                print(e)

        else:
            ret = '无效请求'
        return ret

    def post(self, request):
        """
        上传 小说/文章 的名称
        """
        dat = request.data
        ser = ArticleSerializer(data=dat)
        if ser.is_valid():
            ser.save()
            print('验证成功并保存')
            return HttpResponse(ser.data)
        else:
            print(ser.errors)
            print('验证失败未保存')
            return HttpResponse(ser.errors)
