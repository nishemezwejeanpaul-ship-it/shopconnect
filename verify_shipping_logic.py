import os
import django
import json
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.logistics.models import Region, PickupPoint, ShippingRule
from apps.orders.models import DeliveryMethod
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.orders.views import ShippingCalculationView
from apps.users.models import User

# Custom encoder to handle Decimals in test output
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)

def run_test():
    factory = APIRequestFactory()
    view = ShippingCalculationView.as_view()
    
    # Get test user
    user = User.objects.first()
    
    # Get regions
    rohero = Region.objects.get(name="Rohero")
    gitega = Region.objects.get(name="Gitega")
    
    # Get pickup point for Gitega
    pp_gitega = PickupPoint.objects.get(region=gitega)
    
    test_cases = [
        {
            "name": "DOOR_FREE with Rohero (Urban Bujumbura)",
            "data": {"delivery_method_code": "DOOR_FREE", "to_region_id": str(rohero.id)}
        },
        {
            "name": "DOOR_FREE with Gitega (Not Bujumbura)",
            "data": {"delivery_method_code": "DOOR_FREE", "to_region_id": str(gitega.id)}
        },
        {
            "name": "DOOR_EXPRESS with Rohero (Urban Bujumbura)",
            "data": {"delivery_method_code": "DOOR_EXPRESS", "to_region_id": str(rohero.id)}
        },
        {
            "name": "PICKUP_FREE with Gitega + Valid Pickup Point",
            "data": {
                "delivery_method_code": "PICKUP_FREE", 
                "to_region_id": str(gitega.id),
                "pickup_point_id": str(pp_gitega.id)
            }
        },
        {
            "name": "DOOR_EXPRESS with Gitega (Not Bujumbura)",
            "data": {"delivery_method_code": "DOOR_EXPRESS", "to_region_id": str(gitega.id)}
        }
    ]

    for case in test_cases:
        print(f"\n--- Testing: {case['name']} ---")
        request = factory.post('/api/orders/calculate-shipping/', case['data'], format='json')
        force_authenticate(request, user=user)
        response = view(request)
        response.render()
        print(json.dumps(response.data, indent=2, ensure_ascii=False, cls=DecimalEncoder))

if __name__ == "__main__":
    run_test()
