from django.test import TestCase
from django.db.models import Sum
from .labs import LABORATORIES
from .models import H34vvyUser, Entry

class RankingTests(TestCase):
    databases = {"h34vvy_u53rzz"}

    def setUp(self):
        # labs.py defined keys: lab_nakamura, lab_sato, ...
        self.lab_a_id = "lab_nakamura"
        self.lab_b_id = "lab_sato"

        # Lab A: 30 points
        self.u1 = H34vvyUser.objects.create_user(
            username="u1", password="pw", laboratory=self.lab_a_id
        )
        self.u1.points = 10
        self.u1.save()

        self.u2 = H34vvyUser.objects.create_user(
            username="u2", password="pw", laboratory=self.lab_a_id
        )
        self.u2.points = 20
        self.u2.save()

        # Lab B: 5 points
        self.u3 = H34vvyUser.objects.create_user(
            username="u3", password="pw", laboratory=self.lab_b_id
        )
        self.u3.points = 5
        self.u3.save()

        # No Lab: 100 points
        self.u4 = H34vvyUser.objects.create_user(username="u4", password="pw")
        self.u4.points = 100
        self.u4.save()

    def test_ranking_aggregation(self):
        # Multiple users in lab_a (10 + 20 = 30 points)
        # Multiple users in lab_b (5 points)
        # Expected: 1 entry for lab_a, 1 entry for lab_b (plus potentially empty lab)
        
        lab_stats = list(
            H34vvyUser.objects.values("laboratory")
            .annotate(total_points=Sum("points"))
            .order_by("-total_points")
        )
        
        # If aggregation fails (due to default ordering), we might see multiple entries for the same lab
        # e.g. Lab A (10), Lab A (20) instead of Lab A (30)
        
        lab_a_entries = [x for x in lab_stats if x["laboratory"] == self.lab_a_id]
        lab_b_entries = [x for x in lab_stats if x["laboratory"] == self.lab_b_id]
        
        print(f"DEBUG: Lab Stats: {lab_stats}")
        
        self.assertEqual(len(lab_a_entries), 1, "Should have exactly one entry for Lab A")
        self.assertEqual(lab_a_entries[0]["total_points"], 30, "Lab A should have 30 points total")
        
        self.assertEqual(len(lab_b_entries), 1, "Should have exactly one entry for Lab B")
        self.assertEqual(lab_b_entries[0]["total_points"], 5, "Lab B should have 5 points total")

    def test_signup_view_with_lab(self):
        response = self.client.post(
            "/h34vvy_u53rzz/signup/",
            {
                "username": "newuser",
                "password1": "password123",
                "password2": "password123",
                "laboratory": self.lab_a_id,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(H34vvyUser.objects.filter(username="newuser").exists())
        user = H34vvyUser.objects.get(username="newuser")
        self.assertEqual(user.laboratory, self.lab_a_id)
