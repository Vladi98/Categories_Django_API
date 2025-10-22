# categories/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, CategorySimilarity


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'depth_display', 'children_count', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at', 'parent']
    readonly_fields = ['created_at', 'updated_at', 'depth_display', 'ancestors_display']

    def children_count(self, obj):
        return obj.children.count()
    children_count.short_description = 'Children'

    def depth_display(self, obj):
        return obj.get_depth()
    depth_display.short_description = 'Depth'
    
    def ancestors_display(self, obj):
        """Display the full path from root to this category."""
        ancestors = obj.get_ancestors()
        if not ancestors:
            return "Root category"
        
        path = " → ".join([a.name for a in ancestors])
        return format_html('<span style="color: #666;">{}</span>', path)
    ancestors_display.short_description = 'Path from Root'


@admin.register(CategorySimilarity)
class CategorySimilarityAdmin(admin.ModelAdmin):
    list_display = ['category_a', 'category_b', 'created_at']
    list_filter = ['created_at']
    search_fields = ['category_a__name', 'category_b__name']
    readonly_fields = ['created_at']
    autocomplete_fields = ['category_a', 'category_b']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['category_a'].label = "First Category"
        form.base_fields['category_b'].label = "Second Category"
        return form
