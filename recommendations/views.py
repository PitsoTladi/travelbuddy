
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from destinations.models import Destination
from destinations.serializers import DestinationSerializer

from events.models import Event
from events.serializers import EventSerializer

from datetime import date


class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        user_interests = set(
            user.interests.values_list('id', flat=True)
        )

        city = request.query_params.get('city')

        recommendations = []

        # -------------------------
        # DESTINATION RECOMMENDATIONS
        # -------------------------

        destinations = Destination.objects.all()

        if city:
            destinations = destinations.filter(city__iexact=city)

        for destination in destinations:
            score = 0

            # Matching interest
            if destination.interest_id in user_interests:
                score += 50

            # Within budget
            if destination.price <= user.budget:
                score += 20

            # Rating
            if destination.rating:
                score += float(destination.rating) * 2

            recommendations.append({
                'type': 'destination',
                'score': score,
                'object': destination
            })

        # -------------------------
        # EVENT RECOMMENDATIONS
        # -------------------------

        events = Event.objects.filter(
            start_date__gte=date.today()
        )

        if city:
            events = events.filter(city__iexact=city)

        for event in events:
            score = 0

            event_interests = set(
                event.interest.values_list('id', flat=True)
            )

            # Matching interest
            if user_interests.intersection(event_interests):
                score += 50

            # Within budget
            if event.price <= user.budget:
                score += 20

            # Base score
            score += 10

            recommendations.append({
                'type': 'event',
                'score': score,
                'object': event
            })

        # -------------------------
        # SORT
        # -------------------------

        recommendations.sort(
            key=lambda item: item['score'],
            reverse=True
        )

        # -------------------------
        # SERIALIZE
        # -------------------------

        response = []

        for item in recommendations:
            response.append({
                'type': item['type'],
                'score': item['score'],
                'data': (
                    DestinationSerializer(item['object']).data
                    if item['type'] == 'destination'
                    else EventSerializer(item['object']).data
                )
            })

        return Response(response)