#!/usr/bin/env python
"""
Test Data Generation Script

Creates sample category tree and similarity relationships for testing.
Run with: python manage.py shell < generate_test_data.py
"""

import os
import django
import random

# Setup Django (uncomment if running standalone)
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
# django.setup()

from categories_app.models import Category, CategorySimilarity


def clear_existing_data():
    """Clear all existing categories and similarities."""
    print("Wiping everything...")
    CategorySimilarity.objects.all().delete()
    Category.objects.all().delete()
    print("Done.")


def create_sample_tree():
    """Create a sample category tree."""
    print("\nCreating sample category tree...")
    
    # Root categories
    electronics = Category.objects.create(
        name="Electronics",
        description="Electronic devices and components"
    )
    
    clothing = Category.objects.create(
        name="Clothing",
        description="Apparel and fashion items"
    )
    
    home = Category.objects.create(
        name="Home & Garden",
        description="Home improvement and gardening"
    )
    
    sports = Category.objects.create(
        name="Sports & Outdoors",
        description="Sports equipment and outdoor gear"
    )
    
    print(f"Created 4 root cats")
    
    # Electronics subcats
    computers = Category.objects.create(
        name="Computers",
        description="Desktop and laptop computers",
        parent=electronics
    )
    
    phones = Category.objects.create(
        name="Mobile Phones",
        description="Smartphones and feature phones",
        parent=electronics
    )
    
    audio = Category.objects.create(
        name="Audio",
        description="audio equipment",
        parent=electronics
    )
    
    gaming = Category.objects.create(
        name="Gaming",
        description="Video games and gaming equipment",
        parent=electronics
    )
    
    #Computers subcats
    laptops = Category.objects.create(
        name="Laptops",
        description="Portable PC",
        parent=computers
    )
    
    desktops = Category.objects.create(
        name="Desktops",
        description="Desktop PC",
        parent=computers
    )
    
    accessories = Category.objects.create(
        name="PC Accessories",
        description="Keyboards, mice, and other accessories",
        parent=computers
    )
    
    # Gamin subcategories
    consoles = Category.objects.create(
        name="Consoless",
        description="PlayStation, Xbox",
        parent=gaming
    )
    
    pc_games = Category.objects.create(
        name="PC Games",
        description="video games",
        parent=gaming
    )
    
    gaming_acc = Category.objects.create(
        name="Gaming Accessories",
        description="gaming gear",
        parent=gaming
    )
    
    # Clothing subcats
    mens = Category.objects.create(
        name="Men's Clothing",
        description="Clothing for men",
        parent=clothing
    )
    
    womens = Category.objects.create(
        name="Women's Clothing",
        description="Clothing for women",
        parent=clothing
    )
    
    kids = Category.objects.create(
        name="Kids' Clothing",
        description="Clothing for children",
        parent=clothing
    )
    
    # Men's clothing subcats
    mens_shirts = Category.objects.create(
        name="Men's Shirts",
        description="T-shirts, and shirts",
        parent=mens
    )
    
    mens_pants = Category.objects.create(
        name="Men's Pants",
        description="Jeans and casual pants",
        parent=mens
    )
    
    # Sports subcategories
    fitness = Category.objects.create(
        name="Fitness Equipment",
        description="Gym and workout equipment",
        parent=sports
    )
    
    outdoor = Category.objects.create(
        name="Outdoor Recreation",
        description="Outdoor activities",
        parent=sports
    )
    
    team_sports = Category.objects.create(
        name="Team Sports",
        description="Sports equipment",
        parent=sports
    )
    
    # Home subcats
    furniture = Category.objects.create(
        name="Furniture",
        description="Home and office furniture",
        parent=home
    )
    
    kitchen = Category.objects.create(
        name="Kitchen & Dining",
        description="Kitchenware and dining items",
        parent=home
    )
    
    garden = Category.objects.create(
        name="Garden",
        description="Gardening tools and supplies",
        parent=home
    )
    
    print(f"Created category tree with {Category.objects.count()} categories")
    
    return {
        'electronics': electronics,
        'clothing': clothing,
        'home': home,
        'sports': sports,
        'computers': computers,
        'phones': phones,
        'audio': audio,
        'gaming': gaming,
        'laptops': laptops,
        'desktops': desktops,
        'accessories': accessories,
        'consoles': consoles,
        'pc_games': pc_games,
        'gaming_acc': gaming_acc,
        'mens': mens,
        'womens': womens,
        'kids': kids,
        'mens_shirts': mens_shirts,
        'mens_pants': mens_pants,
        'fitness': fitness,
        'outdoor': outdoor,
        'team_sports': team_sports,
        'furniture': furniture,
        'kitchen': kitchen,
        'garden': garden,
    }


def create_sample_similarities(categories):
    """Create sample similarity relationships."""
    print("\nCreating sample similarity relationships...")
    
    similarities = [
        # Gaming related
        (categories['gaming'], categories['consoles']),
        (categories['gaming'], categories['pc_games']),
        (categories['consoles'], categories['gaming_acc']),
        (categories['pc_games'], categories['laptops']),
        
        # Computer related
        (categories['laptops'], categories['desktops']),
        (categories['laptops'], categories['phones']),
        (categories['accessories'], categories['gaming_acc']),
        
        # Audio related
        (categories['audio'], categories['phones']),
        (categories['audio'], categories['gaming_acc']),
        
        # Clothing related
        (categories['mens'], categories['womens']),
        (categories['mens'], categories['kids']),
        (categories['womens'], categories['kids']),
        (categories['mens_shirts'], categories['mens_pants']),
        
        #Sports and outdoor
        (categories['fitness'], categories['outdoor']),
        (categories['fitness'], categories['team_sports']),
        (categories['outdoor'], categories['garden']),
        
        #Home related
        (categories['furniture'], categories['kitchen']),
        (categories['kitchen'], categories['garden']),
        
        #Cross  category similarites
        (categories['gaming'], categories['fitness']),
        (categories['outdoor'], categories['sports']),
        (categories['phones'], categories['fitness']),
    ]
    
    created_count = 0
    for cat_a, cat_b in similarities:

        # This is a bit hacky but works we swap places
        if cat_a.id > cat_b.id:
            cat_a, cat_b = cat_b, cat_a
        
        # Check if already exists
        if not CategorySimilarity.objects.filter(
            category_a=cat_a, category_b=cat_b
        ).exists():
            CategorySimilarity.objects.create(
                category_a=cat_a,
                category_b=cat_b
            )
            created_count += 1
    
    print(f"Created {created_count} similarity relationships")
    print(f"Total similarities: {CategorySimilarity.objects.count()}.")

def create_additional_random_similarities(num_similarities=20):
    pass
    #TODO

def print_summary():
    """Print summaryof data."""
    print("\n" + "=" * 80)
    print("DATA GENERATION COMPLETE")
    print("=" * 80)
    
    total_categories = Category.objects.count()
    total_similarities = CategorySimilarity.objects.count()
    root_categories = Category.objects.filter(parent__isnull=True).count()
    
    print(f"\nTotal categories: {total_categories}")
    print(f"Root categories: {root_categories}")
    print(f"Total similarity relationships: {total_similarities}")
    
    #Calculate depth stats
    depths = {}
    for cat in Category.objects.all():
        depth = cat.get_depth()
        depths[depth] = depths.get(depth, 0) + 1
    
    print("\nCategories by depth:")
    for depth in sorted(depths.keys()):
        print(f"  Depth {depth}: {depths[depth]} categories")
    print("\n" + "=" * 80)


def main():
    """Main function to generate all test data."""
    print("=" * 80)
    print("CATEGORY TREE TEST DATA GENERATOR")
    print("=" * 80)
    
    # Clear existing data
    print("Clearind data... ")
    clear_existing_data()
    
    # Create sample tree
    categories = create_sample_tree()
    
    # Create similarities
    create_sample_similarities(categories)
    
    # # 
    # Print summary
    print_summary()


