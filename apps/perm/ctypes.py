from django.contrib.contenttypes.models import ContentType


def get_content_type(table):
    table_name = table.name
    app_label = table._meta.app_label
    return ContentType.objects.get(app_label=app_label, model=table_name)


def get_default_content_type(obj):
    return ContentType.objects.get_for_model(obj)
