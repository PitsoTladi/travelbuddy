
import os
import django
from datetime import date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelbuddy.settings")
django.setup()

from destinations.models import Destination
from events.models import Event
from interests.models import Interest


# Use existing interests; do not create duplicate interest records.
interests = {
    interest.name.lower(): interest
    for interest in Interest.objects.all()
}

required_interests = ["nature", "adventure", "food", "sports", "art", "nightlife", "music"]
missing = [name for name in required_interests if name not in interests]

if missing:
    raise ValueError(f"Missing interests in database: {missing}")


# Five destinations across the East Rand.
destination_data = [
    {
        "name": "Dries Niemandt Park",
        "city": "Kempton Park",
        "latitude": "-26.107500",
        "longitude": "28.231900",
        "description": "A local outdoor space for recreation, relaxation and community activities.",
        "price": "0.00",
        "interest": interests["nature"],
    },
    {
        "name": "Wild Waters",
        "city": "Boksburg",
        "latitude": "-26.198000",
        "longitude": "28.255000",
        "description": "A waterpark destination for a fun day out with friends and family. Confirm current admission prices before visiting.",
        "price": "250.00",
        "interest": interests["adventure"],
    },
    {
        "name": "Homestead Lake",
        "city": "Benoni",
        "latitude": "-26.171181",
        "longitude": "28.289541",
        "description": "A lakeside location suited to outdoor relaxation, photography and nature appreciation.",
        "price": "0.00",
        "interest": interests["nature"],
    },
    {
        "name": "Korsman Conservancy",
        "city": "Benoni",
        "latitude": "-26.163000",
        "longitude": "28.315000",
        "description": "A nature-focused destination for birdwatching, walking and appreciating local wildlife.",
        "price": "0.00",
        "interest": interests["nature"],
    },
    {
        "name": "Germiston Lake",
        "city": "Germiston",
        "latitude": "-26.229000",
        "longitude": "28.180000",
        "description": "A popular local outdoor area for walking, scenic views and recreational activities.",
        "price": "0.00",
        "interest": interests["sports"],
    },
]

destinations = {}

for item in destination_data:
    data = item.copy()
    name = data.pop("name")
    interest = data.pop("interest")

    destination, created = Destination.objects.update_or_create(
        name=name,
        city=data["city"],
        defaults={
            **data,
            "interest": interest,
        },
    )
    destinations[name] = destination

    print(f"{'Created' if created else 'Updated'} destination: {name}")


# These are fictional demonstration events for testing TravelBuddySA.
# They are not verified real-world event listings.
event_data = [
    {
        "name": "East Rand Sunset Picnic (Demo)",
        "city": "Kempton Park",
        "latitude": "-26.108500",
        "longitude": "28.233000",
        "description": "DEMO EVENT: Bring snacks, meet fellow explorers and enjoy a relaxed sunset picnic.",
        "price": "50.00",
        "category": "Social",
        "destination": destinations["Dries Niemandt Park"],
        "start_date": date(2026, 11, 7),
        "end_date": date(2026, 11, 7),
        "capacity": 30,
        "interests": ["food", "nature", "music"],
    },
    {
        "name": "Boksburg Summer Splash (Demo)",
        "city": "Boksburg",
        "latitude": "-26.199000",
        "longitude": "28.256000",
        "description": "DEMO EVENT: A sample summer adventure outing for friends and waterpark enthusiasts.",
        "price": "100.00",
        "category": "Adventure",
        "destination": destinations["Wild Waters"],
        "start_date": date(2026, 11, 14),
        "end_date": date(2026, 11, 14),
        "capacity": 40,
        "interests": ["adventure", "sports"],
    },
    {
        "name": "Benoni Lakeside Social (Demo)",
        "city": "Benoni",
        "latitude": "-26.172000",
        "longitude": "28.291000",
        "description": "DEMO EVENT: A relaxed lakeside social with conversation, food and outdoor activities.",
        "price": "30.00",
        "category": "Social",
        "destination": destinations["Homestead Lake"],
        "start_date": date(2026, 11, 21),
        "end_date": date(2026, 11, 21),
        "capacity": 25,
        "interests": ["food", "nature", "music"],
    },
    {
        "name": "Germiston Community Skate Day (Demo)",
        "city": "Germiston",
        "latitude": "-26.230000",
        "longitude": "28.181000",
        "description": "DEMO EVENT: A sample community sports meetup for skaters and spectators.",
        "price": "0.00",
        "category": "Sports",
        "destination": destinations["Germiston Lake"],
        "start_date": date(2026, 11, 28),
        "end_date": date(2026, 11, 28),
        "capacity": 35,
        "interests": ["sports", "music"],
    },
    {
        "name": "East Rand Photography Walk (Demo)",
        "city": "Benoni",
        "latitude": "-26.164000",
        "longitude": "28.316000",
        "description": "DEMO EVENT: Practise photography, explore nature and capture interesting local scenery.",
        "price": "20.00",
        "category": "Arts and Culture",
        "destination": destinations["Korsman Conservancy"],
        "start_date": date(2026, 12, 5),
        "end_date": date(2026, 12, 5),
        "capacity": 20,
        "interests": ["art", "nature", "adventure"],
    },
]

for item in event_data:
    data = item.copy()
    name = data.pop("name")
    event_interests = data.pop("interests")

    event, created = Event.objects.update_or_create(
        name=name,
        defaults=data,
    )

    event.interest.set([interests[key] for key in event_interests])

    print(f"{'Created' if created else 'Updated'} event: {name}")


print("\nSeed complete.")
print(f"Destinations in database: {Destination.objects.count()}")
print(f"Events in database: {Event.objects.count()}")
print("Demo events are not confirmed real-world events.")
