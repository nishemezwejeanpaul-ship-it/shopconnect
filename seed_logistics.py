import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.logistics.models import Region, PickupPoint, ShippingRule
from apps.orders.models import DeliveryMethod

def seed():
    print("Seeding delivery methods...")
    methods = [
        { 'code': 'DOOR_FREE',    'name': 'Livraison à domicile',        'is_active': True },
        { 'code': 'PICKUP_FREE',  'name': 'Retrait en point relais',     'is_active': True },
        { 'code': 'DOOR_EXPRESS', 'name': 'Livraison express (2-4h)',    'is_active': True },
    ]
    
    for m in methods:
        DeliveryMethod.objects.update_or_create(code=m['code'], defaults=m)

    print("Seeding regions...")
    # Bujumbura Province
    buj_prov, _ = Region.objects.get_or_create(name="Bujumbura Mairie", type="province")
    
    # Bujumbura City
    buj_city, _ = Region.objects.get_or_create(name="Bujumbura City", type="city", parent=buj_prov)
    
    # Quarters (Urban zones)
    quarters = ["Rohero", "Ngagara", "Cibitoke", "Kinama", "Musaga"]
    quarter_objs = []
    for q in quarters:
        obj, _ = Region.objects.get_or_create(name=q, type="zone", parent=buj_city)
        quarter_objs.append(obj)

    print("Seeding major towns and pickup points...")
    other_towns = ["Gitega", "Ngozi", "Rumonge", "Bururi"]
    for town in other_towns:
        # Create province and city for each town for completeness
        prov, _ = Region.objects.get_or_create(name=f"{town} Province", type="province")
        city, _ = Region.objects.get_or_create(name=town, type="city", parent=prov)
        
        # Create Pickup Point
        PickupPoint.objects.get_or_create(
            name=f"Point Relais {town}",
            region=city,
            address=f"Centre ville de {town}",
            type="partner",
            is_active=True
        )

    print("Seeding shipping rules for DOOR_EXPRESS...")
    express_method = DeliveryMethod.objects.get(code='DOOR_EXPRESS')
    
    # Create rules for urban zones (for simplicity, we'll assume shipping within Bujumbura Mairie)
    # The user says: "Create ShippingRule for DOOR_EXPRESS: Bujumbura urban zones, price between 1000-2000 BIF"
    # Usually a rule is from A to B. If it's local delivery, we can define rules from Bujumbura City to its quarters.
    
    import random
    for q in quarter_objs:
        ShippingRule.objects.get_or_create(
            from_region=buj_city,
            to_region=q,
            delivery_method=express_method,
            defaults={
                'price': random.randint(1000, 2000),
                'estimated_days': 0, # Same day
                'currency': 'BIF'
            }
        )

    print("Logistics seeding completed!")

if __name__ == "__main__":
    seed()
