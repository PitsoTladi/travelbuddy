from .views import InterestViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("interests", InterestViewSet)

urlpatterns = router.urls
