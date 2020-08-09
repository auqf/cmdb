
from django.conf.urls import url, include

from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter(trailing_slash=False)
router.register("data-lucene", views.DataLuceneViewSet, basename="data-lucene")
router.register("deleted-data-lucene", views.DeletedDataLuceneViewset, basename="deleted-data-lucene")
router.register("data-dsl", views.DataDSLViewSet, basename="data-dsl")
router.register("deleted-data-dsl", views.DeleteDataDSLViewSet, basename="deleted-data-dsl")


urlpatterns = [
    url(r'^', include(router.urls))
]
