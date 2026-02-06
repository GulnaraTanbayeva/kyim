from django.core.management.base import BaseCommand
from core.models import MyList, Product
from userauths.models import User
from faker import Faker
import random

fake = Faker()

class Command(BaseCommand):
    help = 'Generate fake values for MyList model'

    def handle(self, *args, **options):
        users = User.objects.all()
        products = Product.objects.all()

        # Define the number of fake entries to generate
        num_fake_entries = 100  # Adjust as needed

        for _ in range(num_fake_entries):
            # Choose a random user and product
            user = random.choice(users)
            product = random.choice(products)

            # Check if the user has already added the product to their list
            existing_entry = MyList.objects.filter(user=user, product=product).exists()

            # If the entry already exists, skip to the next iteration
            if existing_entry:
                continue

            # Create a new entry in MyList with a random liked status
            MyList.objects.create(
                user=user,
                product=product,
                paid_status=False,
                liked=True
            )

        self.stdout.write(self.style.SUCCESS(f'{num_fake_entries} fake entries generated successfully for MyList model!'))