# categories/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from .models import Category, CategorySimilarity
from .serializers import (
    CategoryListSerializer,
    CategoryDetailSerializer,
    CategoryCreateUpdateSerializer,
    CategoryTreeSerializer,
    CategorySimilaritySerializer,
    CategorySimilarityCreateSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category CRUD and tree operations.
    
    list: Get all categories (you cab filter by parent, depth)
    retrieve: Get detailed information about a specific category
    create: Create a new category
    update: Update a category
    destroy: Delete a category (cascades to children)
    tree: Get the entire category tree structure
    roots: Get all root categories (no parent)
    children: Get children of a specific category
    move: Move a category to a new parent
    """
    queryset = Category.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateUpdateSerializer
        elif self.action == 'tree':
            return CategoryTreeSerializer
        return CategoryDetailSerializer
    
    def get_queryset(self):
        queryset = Category.objects.all()
        
        # Filter by parent query paramm
        parent_id = self.request.query_params.get('parent', None)
        if parent_id is not None:
            queryset = queryset.filter(parent_id=parent_id)

        # TODO: this depth filtering in Python is inefficient for huge trees but for our use case it is ok
        # could use raw SQL or denormalize depth into a field
        depth = self.request.query_params.get('depth', None)
        
        if depth is not None:
            try:
                depth = int(depth)
                #Get all categories and filter by depth in Python
                category_ids = [
                    cat.id for cat in queryset 
                    if cat.get_depth() == depth
                ]
                queryset = queryset.filter(id__in=category_ids)
            except ValueError:
                pass
        
        #Search by name (LIKE "STR_TEXT" in plain Sql)
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        # prefetch_related for optimiezed queries
        # without these you get 1000+ queries on list view
        return queryset.select_related('parent').prefetch_related('children')
    
    @action(detail=False, methods=['get'])
    def tree(self, req):
        """Get the entire category tree starting from root cat"""
        roots = Category.objects.filter(parent__isnull=True).prefetch_related('children')
        serializer = CategoryTreeSerializer(roots, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def roots(self, request):
        roots = Category.objects.filter(parent__isnull=True)
        serializer = CategoryListSerializer(roots, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        category = self.get_object()
        children = category.children.all()
        serializer = CategoryListSerializer(children, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def descendants(self, request, pk=None):
        category = self.get_object()
        descendants = category.get_descendants()
        serializer = CategoryListSerializer(descendants, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def ancestors(self, request, pk=None):
        category = self.get_object()
        ancestors = category.get_ancestors()
        serializer = CategoryListSerializer(ancestors, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """Move a category to a new parent"""
        category = self.get_object()
        new_parent_id = request.data.get('parent')
        
        if new_parent_id is None:
            category.parent = None
            category.save()
            serializer = CategoryDetailSerializer(category)
            return Response(serializer.data)
        
        try:
            new_parent = Category.objects.get(id=new_parent_id)
        except Category.DoesNotExist:
            return Response({'error': 'Parent not found'}, status=404)
        
        # basic validation
        if new_parent == category:
            return Response({'error': 'Cannot move to itself'}, status=400)
        
        if new_parent in category.get_descendants():
            return Response({'error': 'Cannot move to descendant'}, status=400)
        
        category.parent = new_parent
        category.save()
        
        return Response(CategoryDetailSerializer(category).data)
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """Get all categories similar to this category."""
        category = self.get_object()
        similar_categories = CategorySimilarity.get_similar_categories(category)
        serializer = CategoryListSerializer(similar_categories, many=True)
        return Response(serializer.data)


class CategorySimilarityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing category similarity relationships.
    
    list: Get all similarity relationships
    retrieve: Get a specific similarity relationship
    create: Create a new similarity relationship
    destroy: Delete a similarity relationship
    by_category: Get all similarities for a specific category
    """
    queryset = CategorySimilarity.objects.all()
    serializer_class = CategorySimilaritySerializer
    
    def get_queryset(self):
        # both category_a and category_b are FK, so select_related works
        # saves us from doing N additional queries when serializing
        queryset = CategorySimilarity.objects.all().select_related(
            'category_a', 'category_b'
        )
        
        # Filter by cat
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(
                Q(category_a_id=category_id) | Q(category_b_id=category_id)
            )
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = CategorySimilarityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        similarity = serializer.save()
        
        output_serializer = CategorySimilaritySerializer(similarity)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        similarities_data = request.data.get('similarities', [])
        
        created = []
        errors = []
        
        for sim_data in similarities_data:
            serializer = CategorySimilarityCreateSerializer(data=sim_data)
            if serializer.is_valid():
                similarity = serializer.save()
                created.append(CategorySimilaritySerializer(similarity).data)
            else:
                errors.append({
                    'data': sim_data,
                    'errors': serializer.errors
                })
        
        return Response({
            'created': created,
            'errors': errors,
            'created_count': len(created),
            'error_count': len(errors)
        }, status=status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get all similarity relationships for a specific category."""
        category_id = request.query_params.get('category_id')
        
        if not category_id:
            return Response(
                {'error': 'category_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response(
                {'error': 'Category does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        similarities = CategorySimilarity.objects.filter(
            Q(category_a=category) | Q(category_b=category)
        ).select_related('category_a', 'category_b')
        
        serializer = CategorySimilaritySerializer(similarities, many=True)
        return Response(serializer.data)
