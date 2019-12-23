from rest_framework.pagination import PageNumberPagination

# 重写分页类，重写参数的名称pageSize（数据量）和pageNum（当前页）
class MyPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'pageSize'
    page_query_param = 'pageNum'