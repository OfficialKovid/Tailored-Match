import json
from django.core.management.base import BaseCommand
from products.models import Shirt

class Command(BaseCommand):
    help = 'Load shirts data from JSON file'

    def handle(self, *args, **kwargs):
        with open('shirts.json') as f:
            shirts_data = json.load(f)

        for item in shirts_data:
            # Create/update shirt
            shirt_obj, created = Shirt.objects.update_or_create(
                pid=item['pid'],
                defaults={
                    'title': item['title'],
                    'price': item['price'],
                    'rating': item.get('rating'),
                    'sizes_listed': json.dumps(item['sizesListed']),
                    'img_url': item['imgUrl'],
                    'url': item['url']
                }
            )

            # Save size chart data if available
            if 'size-chart' in item:
                shirt_obj.save_size_data(item['size-chart'])

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(shirts_data)} shirts'))
