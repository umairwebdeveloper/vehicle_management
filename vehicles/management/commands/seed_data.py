import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from django.contrib.auth import get_user_model
from vehicles.models import Vehicle
from forum.models import Post, CAT_CHOICES
from logs.models import MaintenanceLog, Expense
User = get_user_model()


class Command(BaseCommand):
    help = (
        "Seed database with dummy Users, Vehicles, MaintenanceLogs, Expenses and Posts"
    )

    def handle(self, *args, **options):
        fake = Faker()
        self.stdout.write("Deleting old data…")
        Post.objects.all().delete()
        Expense.objects.all().delete()
        MaintenanceLog.objects.all().delete()
        Vehicle.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        self.stdout.write("Creating users…")
        users = []
        for _ in range(10):
            user = User.objects.create_user(
                username=fake.user_name(), email=fake.email(), password="password123"
            )
            users.append(user)

        self.stdout.write("Creating vehicles, logs, expenses and posts…")
        for user in users:
            # each user gets 1–3 vehicles
            for _ in range(random.randint(1, 3)):
                vehicle = Vehicle.objects.create(
                    owner=user,
                    reg_number=fake.bothify(
                        text="??##???", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    ),
                    make=fake.company(),
                    model=fake.word().title(),
                    year=random.randint(2000, timezone.now().year),
                    vin=fake.bothify(
                        text="?" * 17, letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                    ),
                )

                # Maintenance logs: 3–6 entries per vehicle
                for _ in range(random.randint(3, 6)):
                    dt = fake.date_between(start_date="-2y", end_date="today")
                    MaintenanceLog.objects.create(
                        vehicle=vehicle,
                        date=dt,
                        mileage=random.randint(5_000, 150_000),
                        service_type=random.choice(
                            [
                                c[0]
                                for c in MaintenanceLog._meta.get_field(
                                    "service_type"
                                ).choices
                            ]
                        ),
                        notes=fake.sentence(nb_words=8),
                    )

                # Expenses: 4–8 entries per vehicle
                for _ in range(random.randint(4, 8)):
                    dt = fake.date_between(start_date="-2y", end_date="today")
                    Expense.objects.create(
                        vehicle=vehicle,
                        date=dt,
                        category=random.choice(
                            [c[0] for c in Expense._meta.get_field("category").choices]
                        ),
                        amount=round(random.uniform(20.0, 500.0), 2),
                        notes=fake.sentence(nb_words=6),
                    )

                # Posts: 2–5 per vehicle
                for _ in range(random.randint(2, 5)):
                    created_dt = fake.date_time_between(
                        start_date="-1y",
                        end_date="now",
                        tzinfo=timezone.get_current_timezone(),
                    )
                    post = Post.objects.create(
                        author=user,
                        vehicle=vehicle if random.choice([True, False]) else None,
                        cat=random.choice([c[0] for c in CAT_CHOICES]),
                        title=fake.sentence(nb_words=6),
                        body=fake.paragraph(nb_sentences=3),
                        created=created_dt,
                        solved=random.choice([True, False]),
                        share_vehicle=random.choice([True, False]),
                    )
        self.stdout.write(self.style.SUCCESS("✅ Database successfully seeded"))
