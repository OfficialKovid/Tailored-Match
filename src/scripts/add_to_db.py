import os
import django
import json
from decimal import Decimal

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tailored_match.settings")
django.setup()

from products.models import Shirt, Size, SizeChart

def validate_measurements(size_data):
    """Check if all required measurements are present and not null"""
    required_measurements = ['chest', 'shoulder', 'length', 'sleeve-length']
    for measurement in required_measurements:
        if measurement not in size_data or size_data[measurement] is None:
            return False
    return True

def load_shirts():
    # Clear existing data
    Shirt.objects.all().delete()

    # Load JSON data
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data", "shirts.json")
    with open(json_path, 'r', encoding='utf-8') as file:
        shirts_data = json.load(file)

    # Process each shirt
    for shirt_data in shirts_data:
        # Check if size chart exists and has valid data
        size_chart = shirt_data.get('size-chart', {})
        if not size_chart:
            continue

        # Check if at least one size has complete measurements
        valid_sizes = False
        for size_name, measurements in size_chart.items():
            if validate_measurements(measurements):
                valid_sizes = True
                break

        if not valid_sizes:
            continue

        # Create shirt object
        try:
            price_str = shirt_data['price'].replace('₹', '').replace(',', '').strip()
            shirt = Shirt.objects.create(
                pid=shirt_data['pid'],
                title=shirt_data['title'],
                price=price_str,
                rating=shirt_data['rating'] if shirt_data['rating'] else None,
                sizes_listed=json.dumps(shirt_data['sizesListed']),
                img_url=shirt_data['imgUrl'],
                url=shirt_data['url']
            )

            # Create sizes and measurements
            for size_name, measurements in size_chart.items():
                if not validate_measurements(measurements):
                    continue

                size = Size.objects.create(
                    shirt=shirt,
                    size_name=size_name
                )

                # Convert measurements to decimal, handling string ranges
                chest = measurements['chest']
                if isinstance(chest, str) and '-' in chest:
                    chest = chest.split('-')[0]  # Take the smaller value
                
                shoulder = measurements['shoulder']
                if isinstance(shoulder, str) and '-' in shoulder:
                    shoulder = shoulder.split('-')[0]
                
                length = measurements['length']
                if isinstance(length, str) and '-' in length:
                    length = length.split('-')[0]
                
                sleeve = measurements['sleeve-length']
                if isinstance(sleeve, str) and '-' in sleeve:
                    sleeve = sleeve.split('-')[0]

                try:
                    SizeChart.objects.create(
                        size=size,
                        chest=Decimal(str(chest).strip()),
                        shoulder=Decimal(str(shoulder).strip()),
                        length=Decimal(str(length).strip()),
                        sleeve_length=Decimal(str(sleeve).strip())
                    )
                except (ValueError, TypeError):
                    size.delete()
                    continue

            print(f"Added shirt: {shirt.title}")

        except Exception as e:
            print(f"Error processing shirt {shirt_data['pid']}: {str(e)}")
            continue

if __name__ == "__main__":
    load_shirts()
    print("Database population completed!")
