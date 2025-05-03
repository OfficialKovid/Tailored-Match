import os
import django
import json
from decimal import Decimal

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tailored_match.settings")
django.setup()

from products.models import Shirt, Size, SizeChart

def load_shirts():
    # Clear existing data
    print("Clearing existing data...")
    Shirt.objects.all().delete()
    successful_entries = 0
    total_shirts = 0

    # Load JSON data
    print("Loading JSON data...")
    with open('tshirt.json', 'r', encoding='utf-8') as file:
        shirts_data = json.load(file)
        total_shirts = len(shirts_data)

    print(f"Found {total_shirts} shirts in JSON file")
    print("Starting database population...")

    for shirt_data in shirts_data:
        try:
            # Clean price string
            price_str = shirt_data['price'].replace('₹', '').replace(',', '').strip()
            
            # Create shirt object
            shirt = Shirt.objects.create(
                pid=shirt_data['pid'],
                title=shirt_data['title'],
                price=price_str,
                rating=shirt_data['rating'] if shirt_data['rating'] else None,
                sizes_listed=json.dumps(shirt_data['sizesListed']),
                img_url=shirt_data['imgUrl'],
                url=shirt_data['url']
            )

            # Create sizes for each listed size
            for size_name in json.loads(shirt.sizes_listed):
                size = Size.objects.create(
                    shirt=shirt,
                    size_name=size_name
                )

            successful_entries += 1
            if successful_entries % 10 == 0:  # Print progress every 10 shirts
                print(f"Progress: {successful_entries}/{total_shirts} shirts added")
                
        except Exception as e:
            print(f"Error adding shirt {shirt_data.get('pid', 'unknown')}: {str(e)}")
            continue

    # Print final statistics
    print("\n=== Database Population Summary ===")
    print(f"Successfully added {successful_entries} out of {total_shirts} shirts")
    print(f"Success rate: {(successful_entries/total_shirts)*100:.2f}%")
    print("\nDatabase Statistics:")
    print(f"Total shirts: {Shirt.objects.count()}")
    print(f"Total sizes: {Size.objects.count()}")

if __name__ == "__main__":
    load_shirts()
