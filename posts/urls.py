from rest_framework.routers  import DefaultRouter
from .views import postViewSet

router = DefaultRouter()
router.register('posts',postViewSet)
urlpatterns =  router.urls

