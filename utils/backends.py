from django.utils.encoding import force_str
from rest_framework.compat import coreapi, coreschema
from rest_framework.filters import SearchFilter


class MySearchFilter(SearchFilter):
    """
    借助代码，自动生成文档，search搜索字段明确化
    """
    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
            coreapi.Field(
                name=self.search_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_str(self.search_title),
                    description=self.get_search_description(view)
                )
            )
        ]

    def get_schema_operation_parameters(self, view):
        return [
            {
                'name': self.search_param,
                'required': False,
                'in': 'query',
                'description': self.get_search_description(view),
                'schema': {
                    'type': 'string',
                },
            },
        ]

    def get_search_description(self, view):
        return f'搜索字段: {force_str(self.get_search_fields(view, None))}'
