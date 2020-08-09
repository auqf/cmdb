from rest_framework import serializers


class EmptySerializer(serializers.BaseSerializer):
    """
    有时viewset的某个action不需要任何Serializer（如，删除时只需要一个pk），
    为了避免额外的参数在自动生成的api文档中带来困惑，可使用这个空Serializer
    """
