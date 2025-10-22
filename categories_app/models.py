# categories/models.py
from django.db import models
from django.core.exceptions import ValidationError

class Category(models.Model):
    """
    Category model supporting hierarchical tree structure.
    Uses adjacency list pattern for simplicity and maintainability.
    """
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['parent', 'name']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Prevent circullar references in the tree."""
        # can't be your own parent obviously
        if self.parent and self.parent == self:
            raise ValidationError("A category cannot be its own parent.")

        # check for circular refs - walk up the tree
        ancestor = self.parent
        while ancestor:
            if ancestor == self:
                raise ValidationError("Circular reference detected!")
            ancestor = ancestor.parent

    def get_ancestors(self):
        ancestors = []
        current = self.parent
        while current:
            ancestors.insert(0, current)
            current = current.parent
        return ancestors

    def get_descendants(self):
        descendants = []
        queue = list(self.children.all())
        while queue:
            child = queue.pop(0)
            descendants.append(child)
            queue.extend(child.children.all())
        return descendants

    def get_depth(self):
        depth = 0
        current = self.parent
        while current:
            depth += 1
            current = current.parent
        return depth


class CategorySimilarity(models.Model):
    """
    similarity in bith directions relationship between categories.
    Stores only one direction (loweest id is first) to avoid duplicates.
    """
    # bit of a hack but cleaner than ManyToMany with custom through
    category_a = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='similarities_a', 
        db_index=True
    )
    category_b = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='similarities_b',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('category_a', 'category_b')
        indexes = [
            models.Index(fields=['category_a', 'category_b']),
            models.Index(fields=['category_b', 'category_a']),
        ]

    def clean(self):
        """Ensure category_a.id < category_b.id and make sure they are diff"""
        if self.category_a == self.category_b:
            raise ValidationError("A category cannot be similar to itself.")
        
        # Enforce ordering: lower id first
        if self.category_a.id and self.category_b.id:
            if self.category_a.id > self.category_b.id:
                self.category_a, self.category_b = self.category_b, self.category_a

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category_a.name} <-> {self.category_b.name}"

    @classmethod
    def get_similar_categories(cls, category):
        """Get all categories similar to a  given category."""
        from django.db.models import Q
        
        # use this Q class to filter based on 2 or more criterias
        smilarities = cls.objects.filter(
            Q(category_a=category) | Q(category_b=category)
        ).select_related('category_a', 'category_b')
        
        similar_ids = set()
        for sim in smilarities:
            if sim.category_a.id == category.id:
                similar_ids.add(sim.category_b.id)
            else:
                similar_ids.add(sim.category_a.id)
        
        return Category.objects.filter(id__in=similar_ids)

    @classmethod
    def are_similar(cls, cat_a, cat_b):
        """Check if two categories are similar."""
        if cat_a.id == cat_b.id:
            return False
        
        min_id, max_id = sorted([cat_a.id, cat_b.id])
        return cls.objects.filter(
            category_a_id=min_id,
            category_b_id=max_id
        ).exists()