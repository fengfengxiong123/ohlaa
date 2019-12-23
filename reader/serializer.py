from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.Serializer):  # 小说基本信息表序列化
    id = serializers.IntegerField()
    art_name = serializers.CharField()
    art_add_date = serializers.DateTimeField(read_only=True, format="%Y-%m-%d")
    art_author = serializers.CharField()
    user_owner_id = serializers.CharField(source='user_owner.id', read_only=True)
    user_owner_username = serializers.CharField(source='user_owner.username', read_only=True)
    art_type = serializers.CharField()
    art_status = serializers.CharField()
    art_introduction = serializers.CharField()
    art_name_used = serializers.CharField()
    art_hits = serializers.CharField()

    art_hots = serializers.CharField()

    def create(self, validated_data):
        validated_data.update(user_owner_id=1)
        article = Article.objects.create(**validated_data)
        return article
