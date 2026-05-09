import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User, Shop, Seller
from apps.catalog.models import Category, Product, ProductImage
import random
from django.utils.text import slugify

def seed():
    # 1. Ensure we have a user and a shop
    user, created = User.objects.get_or_create(
        email='admin@example.com',
        defaults={'phone': '1234567890', 'is_staff': True, 'is_superuser': True}
    )
    if created:
        user.set_password('admin123')
        user.save()
        print("Created admin user")

    seller, created = Seller.objects.get_or_create(
        user=user,
        defaults={'is_verified': True}
    )

    shop, created = Shop.objects.get_or_create(
        seller=seller,
        defaults={'name': 'My Super Shop', 'slug': 'my-super-shop', 'is_active': True}
    )
    
    # 2. Categories
    categories_data = [
        {"name": "Électronique", "photo_url": "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=800&q=80"},
        {"name": "Mode & Vêtements", "photo_url": "https://images.unsplash.com/photo-1445205170230-053b83016050?w=800&q=80"},
        {"name": "Maison & Jardin", "photo_url": "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=800&q=80"},
        {"name": "Beauté & Santé", "photo_url": "https://images.unsplash.com/photo-1522335789203-aabd1fc54c28?w=800&q=80"},
        {"name": "Sports & Loisirs", "photo_url": "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=800&q=80"}
    ]

    categories = []
    for c_data in categories_data:
        cat, _ = Category.objects.get_or_create(
            slug=slugify(c_data["name"]),
            defaults={"name": c_data["name"], "photo_url": c_data["photo_url"], "sort_order": 0}
        )
        categories.append(cat)
    print("Created categories")

    # 3. Products
    products_data = [
        # Electronics
        ("Smartphone XYZ Pro", "Un smartphone très performant avec appareil photo exceptionnel.", 500000, 450000, "Électronique", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&q=80"),
        ("Ordinateur Portable Ultra", "PC portable pour les pros. SSD 1 To, 16 Go RAM.", 1200000, 1100000, "Électronique", "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80"),
        ("Écouteurs Sans Fil", "Son de haute qualité avec réduction de bruit active.", 80000, None, "Électronique", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80"),
        
        # Fashion
        ("T-shirt en Coton Premium", "T-shirt très confortable 100% coton bio.", 15000, None, "Mode & Vêtements", "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=800&q=80"),
        ("Robe d'Été Fleurie", "Parfaite pour les beaux jours et les soirées d'été.", 35000, 30000, "Mode & Vêtements", "https://images.unsplash.com/photo-1515347619152-477033529367?w=800&q=80"),
        ("Baskets de Course Pro", "Légères et rapides pour la course à pied.", 60000, 50000, "Mode & Vêtements", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80"),

        # Home
        ("Canapé Moderne 3 Places", "Design élégant pour votre salon. Tissu résistant.", 850000, None, "Maison & Jardin", "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&q=80"),
        ("Lampe de Bureau LED Tactile", "Lumière ajustable avec 3 niveaux de luminosité.", 25000, None, "Maison & Jardin", "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800&q=80"),

        # Beauty
        ("Crème Hydratante Bio", "Prenez soin de votre peau avec cette crème naturelle.", 18000, None, "Beauté & Santé", "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=800&q=80"),
        ("Parfum Élégant pour Femme", "Fragrance longue durée aux notes florales.", 90000, 85000, "Beauté & Santé", "https://images.unsplash.com/photo-1594035910387-fea47794261f?w=800&q=80"),

        # Sports
        ("Ballon de Football Pro", "Taille 5 standard, haute qualité pour l'entraînement.", 20000, None, "Sports & Loisirs", "https://images.unsplash.com/photo-1614632537423-1e6c2e7e0aab?w=800&q=80"),
        ("Tapis de Yoga Écologique", "Antidérapant, sans PVC.", 15000, None, "Sports & Loisirs", "https://images.unsplash.com/photo-1601122496300-927bb4556488?w=800&q=80"),
    ]

    for p_name, p_desc, p_price, p_discount, cat_name, img_url in products_data:
        cat = next(c for c in categories if c.name == cat_name)
        product, p_created = Product.objects.get_or_create(
            slug=slugify(p_name),
            shop=shop,
            defaults={
                "name": p_name,
                "description": p_desc,
                "price": p_price,
                "discount_price": p_discount,
                "category": cat,
                "status": "active",
                "stock_quantity": random.randint(10, 100),
            }
        )
        if p_created:
            ProductImage.objects.create(
                product=product,
                image_url=img_url,
                is_main=True
            )

    print("Created products")
    print("Database seeding completed!")

if __name__ == '__main__':
    seed()
