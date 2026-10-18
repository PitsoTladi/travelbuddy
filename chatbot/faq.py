
import re


FAQS = [
    {
        "keywords": [
            "how do i book an event",
            "how can i book",
            "make a booking",
            "book an event",
            "booking",
            "reserve",
            "reservation",
            "book",
        ],
        "answer": (
            "To book an event, select an event that has booking capacity "
            "available and submit a booking. You cannot book the same event "
            "twice, and events with zero capacity are closed to bookings."
        ),
        "suggestions": ["cancel booking", "event capacity", "events"],
    },
    {
        "keywords": [
            "cancel my booking",
            "cancel a booking",
            "cancel booking",
            "cancellation",
            "cancel",
        ],
        "answer": (
            "You can cancel your own event booking. "
            "You cannot cancel another user's booking."
        ),
        "suggestions": ["book an event", "events"],
    },
    {
        "keywords": [
            "what events are available",
            "upcoming events",
            "find events",
            "browse events",
            "activities",
            "events",
            "event",
        ],
        "answer": (
            "You can browse events on TravelBuddySA. Check an event's details, "
            "date, price and capacity before booking."
        ),
        "suggestions": ["book an event", "cancel booking", "destinations"],
    },
    {
        "keywords": [
            "places to visit",
            "where should i go",
            "find destinations",
            "browse destinations",
            "destinations",
            "destination",
        ],
        "answer": (
            "You can explore destinations on TravelBuddySA. Use the available "
            "filters to find places that match your interests, city and budget."
        ),
        "suggestions": ["events", "interests", "budget"],
    },
    {
        "keywords": [
            "how do reviews work",
            "write a review",
            "leave a review",
            "submit a review",
            "reviews",
            "review",
            "ratings",
            "rating",
            "rate",
        ],
        "answer": (
            "Authenticated users can review and rate destinations and events. "
            "Share your experience to help other travellers."
        ),
        "suggestions": ["destinations", "events", "points"],
    },
    {
        "keywords": [
            "business creator",
            "event creator",
            "adventure seeker",
            "user roles",
            "what are the roles",
            "roles",
            "role",
        ],
        "answer": (
            "TravelBuddySA has three roles: Adventure Seeker, Business Creator "
            "and Event Creator. Business Creators manage their own destinations; "
            "Event Creators manage their own events. All roles can browse, "
            "attend events, create community posts and submit reviews."
        ),
        "suggestions": ["destinations", "events", "reviews"],
    },
    {
        "keywords": [
            "personal recommendations",
            "recommended destinations",
            "my interests",
            "what are my interests",
            "hobbies",
            "interest",
            "interests",
            "recommendations",
            "recommendation",
        ],
        "answer": (
            "TravelBuddySA uses interests to help you discover relevant "
            "destinations and activities. Explore the recommendations and "
            "interest options available on the platform."
        ),
        "suggestions": ["destinations", "events"],
    },
    {
        "keywords": [
            "community posts",
            "create a post",
            "delete my post",
            "edit my post",
            "posts",
            "post",
            "community",
        ],
        "answer": (
            "You can participate in the TravelBuddySA community by creating "
            "posts. You can edit or delete your own posts, but not other "
            "users' posts."
        ),
        "suggestions": ["reviews", "roles"],
    },
    {
        "keywords": [
            "how do points work",
            "earn points",
            "my rank",
            "ranking",
            "points",
            "rank",
            "level",
        ],
        "answer": (
            "TravelBuddySA includes review points and ranks to recognise "
            "community contributions. Points can be earned through activities "
            "such as submitting reviews."
        ),
        "suggestions": ["reviews", "community"],
    },
]


def normalise_message(message):
    """Lowercase the message and remove unnecessary punctuation."""
    message = message.lower().strip()
    message = re.sub(r"[^\w\s]", " ", message)
    return " ".join(message.split())


def find_faq_answer(message):
    """Find the most specific matching FAQ or return a fallback."""
    message = normalise_message(message)

    if not message:
        return {
            "answer": "Please enter a question so I can help.",
            "suggestions": ["destinations", "events", "book an event"],
        }

    best_match = None
    best_score = 0

    for faq in FAQS:
        score = 0

        for keyword in faq["keywords"]:
            normalised_keyword = normalise_message(keyword)

            # Match complete phrases or words, not partial words.
            pattern = r"\b" + re.escape(normalised_keyword) + r"\b"

            if re.search(pattern, message):
                # Longer phrases receive higher scores.
                score = max(score, len(normalised_keyword.split()) * 10)

        if score > best_score:
            best_score = score
            best_match = faq

    if best_match:
        return {
            "answer": best_match["answer"],
            "suggestions": best_match["suggestions"],
        }

    return {
        "answer": (
            "I'm not sure about that yet. I can help with destinations, "
            "events, bookings, reviews, user roles and recommendations."
        ),
        "suggestions": [
            "destinations",
            "events",
            "book an event",
            "reviews",
        ],
    }
