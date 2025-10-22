from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, CategorySimilarityViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'similarities', CategorySimilarityViewSet, basename='similarity')

urlpatterns = [
    path('', include(router.urls)),
]