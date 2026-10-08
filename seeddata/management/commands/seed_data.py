from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from interests.models import Interest
from destinations.models import Destination
from events.models import Event, Attendance
from reviews.models import review
from posts.models import Post


class Command(BaseCommand):
    help = 'Seeds the database with test data for TravelBuddySA'

    def handle(self, *args, **kwargs):

        User = get_user_model()

        self.stdout.write('Seeding TravelBuddySA data...')

        # ==========================================================
        # INTERESTS
        # ==========================================================

        interest_names = [
            'Music',
            'Adventure',
            'Food',
            'Sports',
            'Nature',
            'Art',
            'Motoring',
            'Nightlife',
        ]

        interests = {}

        for name in interest_names:
            interest, created = Interest.objects.get_or_create(
                name=name
            )
            interests[name] = interest

        self.stdout.write(
            self.style.SUCCESS('✓ Interests created')
        )

        # ==========================================================
        # USERS
        # ==========================================================

        users_data = [
            {
                'username': 'seed_seeker',
                'email': 'seed_seeker@travelbuddy.test',
                'name': 'Seed Seeker',
                'role': 'adventure_seeker',
                'budget': 500,
                'interests': ['Adventure', 'Nature', 'Music'],
            },
            {
                'username': 'seed_seeker2',
                'email': 'seed_seeker2@travelbuddy.test',
                'name': 'Seed Seeker 2',
                'role': 'adventure_seeker',
                'budget': 1000,
                'interests': ['Food', 'Art', 'Nightlife'],
            },
            {
                'username': 'seed_business',
                'email': 'seed_business@travelbuddy.test',
                'name': 'Seed Business',
                'role': 'business_creator',
                'budget': 2000,
                'interests': ['Motoring', 'Sports'],
            },
            {
                'username': 'seed_event',
                'email': 'seed_event@travelbuddy.test',
                'name': 'Seed Event Creator',
                'role': 'event_creator',
                'budget': 2000,
                'interests': ['Music', 'Nightlife'],
            },
        ]

        users = {}

        for data in users_data:

            interest_list = data.pop('interests')

            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults=data
            )

            # Make sure the password is usable.
            if created:
                user.set_password('Password123!')
                user.save()

            user.interests.set(
                [interests[name] for name in interest_list]
            )

            users[data['username']] = user

        self.stdout.write(
            self.style.SUCCESS('✓ Users created')
        )

        # ==========================================================
        # DESTINATIONS
        # ==========================================================

        destinations_data = [
            ('Gold Reef City', 'Johannesburg', 450, 4.5, 'Adventure'),
            ('Zoo Lake', 'Johannesburg', 0, 4.0, 'Nature'),
            ('Maboneng Precinct', 'Johannesburg', 200, 4.3, 'Art'),
            ('Soweto Tour', 'Johannesburg', 350, 4.7, 'Adventure'),
            ('Montecasino', 'Johannesburg', 300, 4.2, 'Nightlife'),
            ('Melville', 'Johannesburg', 150, 4.1, 'Food'),
            ('Cradle of Humankind', 'Johannesburg', 500, 4.8, 'Nature'),
            ('Apartheid Museum', 'Johannesburg', 180, 4.6, 'Art'),
            ('Voortrekker Monument', 'Pretoria', 120, 4.4, 'Art'),
            ('Durban Beachfront', 'Durban', 0, 4.5, 'Nature'),
            ('Cape Point', 'Cape Town', 600, 4.9, 'Adventure'),
            ('Gold Reef Motoring Experience', 'Johannesburg', 400, 4.3, 'Motoring'),
        ]

        destinations = []

        for name, city, price, rating, interest_name in destinations_data:

            destination, created = Destination.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'Explore {name} with TravelBuddySA.',
                    'price': price,
                    'rating': rating,
                    'city': city,
                    'interest': interests[interest_name],
                    'created_by': users['seed_business'],
                }
            )

            destinations.append(destination)

        self.stdout.write(
            self.style.SUCCESS('✓ Destinations created')
        )

        # ==========================================================
        # EVENTS
        # ==========================================================

        today = date.today()

        events_data = [
            ('Joburg Jazz Night', 'Music', 'Johannesburg', 300, 30),
            ('Johannesburg Food Festival', 'Food', 'Johannesburg', 250, 45),
            ('Joburg Adventure Run', 'Sports', 'Johannesburg', 150, 60),
            ('Cars & Coffee Joburg', 'Motoring', 'Johannesburg', 100, 75),
            ('Night Market Maboneng', 'Nightlife', 'Johannesburg', 80, 90),
            ('Pretoria Art Festival', 'Art', 'Pretoria', 200, 30),
            ('Durban Beach Festival', 'Nature', 'Durban', 350, 50),
            ('Cape Town Adventure Expo', 'Adventure', 'Cape Town', 500, 70),
            ('Johannesburg Music Festival', 'Music', 'Johannesburg', 400, 100),
            ('Soweto Cultural Festival', 'Art', 'Johannesburg', 180, 120),
        ]

        events = []

        for name, category, city, price, days_from_now in events_data:

            start_date = today + timedelta(days=days_from_now)
            end_date = start_date + timedelta(days=1)

            event, created = Event.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'Experience {name} with TravelBuddySA.',
                    'price': price,
                    'city': city,
                    'category': category,
                    'destination': destinations[0],
                    'start_date': start_date,
                    'end_date': end_date,
                    'capacity': 500,
                    'created_by': users['seed_event'],
                }
            )

            event.interest.set([interests[category]])
            events.append(event)

        self.stdout.write(
            self.style.SUCCESS('✓ Events created')
        )

        # ==========================================================
        # ATTENDANCE
        # ==========================================================

        attendance_data = [
            (users['seed_seeker'], events[0]),
            (users['seed_seeker'], events[1]),
            (users['seed_seeker2'], events[2]),
            (users['seed_seeker2'], events[4]),
        ]

        for user, event in attendance_data:
            Attendance.objects.get_or_create(
                user=user,
                event=event
            )

        self.stdout.write(
            self.style.SUCCESS('✓ Attendance created')
        )

        # ==========================================================
        # REVIEWS
        # ==========================================================

        review_data = [
            (
                users['seed_seeker'],
                destinations[0],
                None,
                5,
                'Absolutely loved it!'
            ),
            (
                users['seed_seeker2'],
                destinations[2],
                None,
                4,
                'Great atmosphere and food.'
            ),
            (
                users['seed_seeker'],
                None,
                events[0],
                5,
                'Amazing music and atmosphere.'
            ),
            (
                users['seed_seeker2'],
                None,
                events[1],
                4,
                'Great event.'
            ),
        ]

        for user, destination, event, rating, content in review_data:

            review.objects.get_or_create(
                created_by=user,
                destination=destination,
                event=event,
                defaults={
                    'rating': rating,
                    'content': content,
                }
            )

        self.stdout.write(
            self.style.SUCCESS('✓ Reviews created')
        )

        # ==========================================================
        # COMMUNITY POSTS
        # ==========================================================

        posts_data = [
            {
                'title': 'Amazing day at Gold Reef City',
                'content': 'Definitely worth visiting!',
                'user': users['seed_seeker'],
                'destination': destinations[0],
            },
            {
                'title': 'Jazz night was incredible',
                'content': 'The atmosphere was fantastic.',
                'user': users['seed_seeker2'],
                'event': events[0],
            },
            {
                'title': 'Maboneng recommendation',
                'content': 'Great place for food and art.',
                'user': users['seed_seeker'],
                'destination': destinations[2],
            },
        ]

        for data in posts_data:

            user = data.pop('user')

            Post.objects.get_or_create(
                title=data['title'],
                defaults={
                    'content': data['content'],
                    'created_by': user,
                    'destination': data.get('destination'),
                    'event': data.get('event'),
                }
            )

        self.stdout.write(
            self.style.SUCCESS('✓ Community posts created')
        )

        # ==========================================================
        # COMPLETE
        # ==========================================================

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                '=========================================='
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                'TravelBuddySA seed data complete!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '=========================================='
            )
        )

        self.stdout.write(
            f'Destinations: {Destination.objects.count()}'
        )

        self.stdout.write(
            f'Events: {Event.objects.count()}'
        )

        self.stdout.write(
            f'Users: {User.objects.count()}'
        )

        self.stdout.write(
            f'Interests: {Interest.objects.count()}'
        )

        self.stdout.write(
            f'Attendance: {Attendance.objects.count()}'
        )

        self.stdout.write(
            f'Reviews: {review.objects.count()}'
        )

        self.stdout.write(
            f'Posts: {Post.objects.count()}'
        )