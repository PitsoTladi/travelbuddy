from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet

router = DefaultRouter()
router.register('reviews', ReviewViewSet)

urlpatterns = router.urls
