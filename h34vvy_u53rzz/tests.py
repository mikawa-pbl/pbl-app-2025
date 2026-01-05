from django.test import TestCase
from django.db.models import Sum
from .models import H34vvyUser, Laboratory

class RankingTests(TestCase):
    databases = {"h34vvy_u53rzz"}

    def setUp(self):
        self.lab_a = Laboratory.objects.create(name="Lab A")
        self.lab_b = Laboratory.objects.create(name="Lab B")

        # Lab A: 30 points
        self.u1 = H34vvyUser.objects.create_user(
            username="u1", password="pw", laboratory=self.lab_a
        )
        self.u1.points = 10
        self.u1.save()

        self.u2 = H34vvyUser.objects.create_user(
            username="u2", password="pw", laboratory=self.lab_a
        )
        self.u2.points = 20
        self.u2.save()

        # Lab B: 5 points
        self.u3 = H34vvyUser.objects.create_user(
            username="u3", password="pw", laboratory=self.lab_b
        )
        self.u3.points = 5
        self.u3.save()

        # No Lab: 100 points
        self.u4 = H34vvyUser.objects.create_user(username="u4", password="pw")
        self.u4.points = 100
        self.u4.save()

    def test_ranking_aggregation(self):
        labs = list(
            Laboratory.objects.annotate(total_points=Sum("h34vvy_users__points"))
            .order_by("-total_points")
            .all()
        )
        
        self.assertEqual(len(labs), 2)
        
        # 1st: Lab A (30pts)
        self.assertEqual(labs[0].name, "Lab A")
        self.assertEqual(labs[0].total_points, 30)
        
        # 2nd: Lab B (5pts)
        self.assertEqual(labs[1].name, "Lab B")
        self.assertEqual(labs[1].total_points, 5)

    def test_signup_view_with_lab(self):
        response = self.client.post(
            "/h34vvy_u53rzz/signup/",
            {
                "username": "newuser",
                "password1": "password123",
                "password2": "password123",
                "laboratory": self.lab_a.id,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(H34vvyUser.objects.filter(username="newuser").exists())
        user = H34vvyUser.objects.get(username="newuser")
        self.assertEqual(user.laboratory, self.lab_a)
