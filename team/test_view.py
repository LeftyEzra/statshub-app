from django.test import TestCase
from django.urls import reverse
from .models import Team, Player, Competition, Venue

class TeamDetailViewTest(TestCase):
    def setUp(self):
        # Create Competition and Venue
        self.competition = Competition.objects.create(name="National League")
        self.venue = Venue.objects.create(name="National Stadium", state_province="Lagos")

        # Create Team
        self.team = Team.objects.create(
            name="Lagos Lions",
            city="Lagos",
            venue=self.venue,
            competitions=self.competition
        )

        # Create Player
        self.player = Player.objects.create(
            team=self.team,
            player_name="Solomon",
            jersey_number=7,
            position="PG",
            height_cm=180,
            weight_kg=75,
            country="Nigeria",
            is_starter=True
        )

    def test_team_detail_view(self):
        url = reverse('team-detail', args=[self.competition.id, self.team.id])  # Adjust if using slug or other identifier
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lagos Lions")
        self.assertContains(response, "Solomon")
        self.assertContains(response, "PG")



        