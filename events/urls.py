from .views import EventViewSet, AttendanceViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("events", EventViewSet)
router.register("attendance",AttendanceViewSet)

urlpatterns = router.urls
