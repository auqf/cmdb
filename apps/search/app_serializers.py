
from rest_framework import serializers


class DataLuceneSerializer(serializers.Serializer):

    SORT_CHOICES = (
        ("asc", "ascending"),
        ("desc", "descending"),
    )
    indices = serializers.ListField(
        default=[], child=serializers.CharField(), help_text="es的索引")
    query = serializers.CharField(
        default="*", label="查询lucene", help_text="lucene格式的搜索语句")
    sort = serializers.DictField(
        child=serializers.ChoiceField(choices=SORT_CHOICES),
        default={"_score": "desc"},
        help_text="排序(dict)")
    page = serializers.IntegerField(
        default=1, min_value=1, label="页码", help_text="页码")
    page_size = serializers.IntegerField(
        default=10, min_value=1, help_text="单页大小")


# class DeletedDataLuceneSerializer(DataLuceneSerializer):
#
#     def validate_indices(self, indices):
#         return list(map(lambda i: i+"..", indices))

class DataDSLSerializer(DataLuceneSerializer):
    query = None
    body = serializers.DictField(label="DSL查询内容")