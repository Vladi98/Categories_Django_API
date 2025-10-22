# categories/serializers.py
from rest_framework import serializers
from .models import Category, CategorySimilarity


class CategoryListSerializer(serializers.ModelSerializer):
    depth = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'depth', 'children_count', 'created_at']
        
    def get_depth(self, obj):
        return obj.get_depth()
    
    def get_children_count(self, obj):
        return obj.children.count()


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Recursive serializer for tree representation."""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'children']
    
    def get_children(self, obj):
        children = obj.children.all()
        return CategoryTreeSerializer(children, many=True).data


class CategoryDetailSerializer(serializers.ModelSerializer):
    depth = serializers.SerializerMethodField()
    ancestors = serializers.SerializerMethodField()
    children = CategoryListSerializer(many=True, read_only=True)
    similar_categories = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'image', 'parent',
            'depth', 'ancestors', 'children', 'similar_categories',
            'created_at', 'updated_at'
        ]
    
    def get_depth(self, obj):
        return obj.get_depth()
    
    def get_ancestors(self, obj):
        ancestors = obj.get_ancestors()
        return [{'id': a.id, 'name': a.name} for a in ancestors]
    
    def get_similar_categories(self, obj):
        similar = CategorySimilarity.get_similar_categories(obj)
        return [{'id': c.id, 'name': c.name} for c in similar]


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'parent']
    
    def validate_parent(self, value):
        """Prevent circular references."""
        if value and self.instance:
            # Check if new parent is a descendant
            descedants = self.instance.get_descendants()
            if value in descedants:
                raise serializers.ValidationError(
                    "Cannot set parent to a descendant category."
                )
        return value


class CategorySimilaritySerializer(serializers.ModelSerializer):
    category_a_name = serializers.CharField(source='category_a.name', read_only=True)
    category_b_name = serializers.CharField(source='category_b.name', read_only=True)
    
    class Meta:
        model = CategorySimilarity
        fields = ['id', 'category_a', 'category_b', 'category_a_name', 'category_b_name', 'created_at']
        read_only_fields = ['created_at']
    
    def validate(self, data):
        """Ensure categories are different and normalize ordering."""
        cat_a = data.get('category_a')
        cat_b = data.get('category_b')
        
        if cat_a == cat_b:
            raise serializers.ValidationError(
                "A category cannot be similar to itself."
            )
        
        # Normalize ordering
        if cat_a.id > cat_b.id:
            data['category_a'], data['category_b'] = cat_b, cat_a
        
        # Check for existing similarity
        if self.instance is None:
            if CategorySimilarity.objects.filter(
                category_a=data['category_a'],
                category_b=data['category_b']
            ).exists():
                raise serializers.ValidationError(
                    "similarity relationship already exists."
                )
        
        return data


class CategorySimilarityCreateSerializer(serializers.Serializer):
    """Alternative serializer for creating similarities with flexible input."""
    category_a = serializers.IntegerField()
    category_b = serializers.IntegerField()
    
    def validate(self, data):
        """Validate that both categories exist and are different."""
        cat_a_id = data.get('category_a')
        cat_b_id = data.get('category_b')
        
        if cat_a_id == cat_b_id:
            raise serializers.ValidationError(
                "category cannot be similar to itself."
            )
        
        try:
            cat_a = Category.objects.get(id=cat_a_id)
            cat_b = Category.objects.get(id=cat_b_id)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Cat do not exist.")

        if cat_a_id > cat_b_id:
            data['category_a'], data['category_b'] = cat_b_id, cat_a_id
         
         
        # Check for existing similarity
        if CategorySimilarity.objects.filter(
            category_a_id=data['category_a'],
            category_b_id=data['category_b']
        ).exists():
            raise serializers.ValidationError(
                "This similar relationship is already present"
            )
        
        return data
    
    def create(self, validated_data):
        return CategorySimilarity.objects.create(
            category_a_id=validated_data['category_a'],
            category_b_id=validated_data['category_b']
        )
