import sys

from rest_framework.routers import SimpleRouter
from . import views


router = SimpleRouter()
router.register("table", views.TableViewset)
router.register("field", views.FieldViewSet)
router.register("user", views.UserViewset)

app_name = "mgmt"

urlpatterns = router.urls


if sys.argv[1] in ['runserver', 'test']:
    from mgmt.service import DynamicTableManager
    DynamicTableManager.on_django_start()
