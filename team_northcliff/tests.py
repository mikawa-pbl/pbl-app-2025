import json
from django.test import TestCase
from django.urls import reverse

from .models import User, Facility, FacilityAccess


class TeamNorthcliffApiEdgeCaseTests(TestCase):
    # テストで team_northcliff DB を使うことを明示
    databases = ['default', 'team_northcliff']

    def test_user_data_view_user_exists(self):
        # ユーザー Alice を作成して API が 200 と正しいデータを返すことを確認
        user = User.objects.using('team_northcliff').create(name='alice', points=5)
        url = reverse('team_northcliff:api_user_data', args=['alice'])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)  # 200(OK)が返ることを確認
        data = json.loads(resp.content.decode())
        self.assertEqual(data.get('user_id'), user.id)
        self.assertEqual(data.get('points'), 5)

    def test_access_facility_insufficient_points(self):
        # ポイント 0 のユーザー Dave がアクセスを試みると 400 を返し、ポイントが減らないこと
        user = User.objects.using('team_northcliff').create(name='dave', points=0)
        facility = Facility.objects.using('team_northcliff').create(facility_id='test', name='テスト施設')

        url = reverse('team_northcliff:api_access_facility', args=['dave'])
        resp = self.client.post(
            url,
            data=json.dumps({'facility_id': facility.id}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)
        data = json.loads(resp.content.decode())
        self.assertIn('error', data)
        # ポイントが減っていないことを確認
        user.refresh_from_db(using='team_northcliff')
        self.assertEqual(user.points, 0)

    def test_access_facility_success_creates_access_and_deducts_point(self):
        # ポイントを持つユーザー Erin がアクセスすると、ポイントが 1 減り、FacilityAccess が作成される
        user = User.objects.using('team_northcliff').create(name='erin', points=2)
        facility = Facility.objects.using('team_northcliff').create(facility_id='cafe2', name='カフェ2')

        url = reverse('team_northcliff:api_access_facility', args=['erin'])
        resp = self.client.post(
            url,
            data=json.dumps({'facility_id': facility.id}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode())
        self.assertTrue(data.get('success'))
        # DB 上のポイントが1減っている
        user.refresh_from_db(using='team_northcliff')
        self.assertEqual(user.points, 1)
        # FacilityAccess レコードが作成されている
        fa = FacilityAccess.objects.using('team_northcliff').filter(user=user, facility=facility).first()
        self.assertIsNotNone(fa)

    def test_point_overflow_on_award(self):
        """
        ポイントが整数上限に近い（大きな値）のユーザーが投稿で +1 されるときの挙動を確認。
        - DB/バックエンドがオーバーフローを許す場合は +1 されることを期待する。
        - DB レベルでエラーが出る場合は DataError/OverflowError を許容してキャッチする。
        """
        from django.db.utils import DataError

        # 多くの DB で 32-bit 上限に相当する値（例: 2**31 - 1）を使う
        max_int32 = 2**31 - 1
        user = User.objects.using('team_northcliff').create(name='maximal', points=max_int32)
        facility = Facility.objects.using('team_northcliff').create(facility_id='libx', name='図書館X')

        url = reverse('team_northcliff:api_create_post', args=['maximal'])
        payload = {'facility_id': facility.id, 'status': 'moderate', 'comment': 'edge overflow test'}

        try:
            resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        except Exception as e:
            # DB 側でエラーが出るケースを許容する（明示的に検査）
            self.assertTrue(isinstance(e, (DataError, OverflowError)))
        else:
            # エラーが出ずに正常終了した場合はポイントが +1 されていること
            self.assertEqual(resp.status_code, 200)
            user.refresh_from_db(using='team_northcliff')
            self.assertEqual(user.points, max_int32 + 1)

    def test_zero_point_user_repeated_consumption_attempts(self):
        """
        ポイント 0 のユーザーが複数回アクセスを試みてもポイントが負にならず、
        毎回アクセス拒否(400)が返ることを確認する（負の値への保護を検証）。
        """
        user = User.objects.using('team_northcliff').create(name='zerojoe', points=0)
        facility = Facility.objects.using('team_northcliff').create(facility_id='kita2', name='北駐車場2')

        url = reverse('team_northcliff:api_access_facility', args=['zerojoe'])

        for _ in range(2):
            resp = self.client.post(
                url,
                data=json.dumps({'facility_id': facility.id}),
                content_type='application/json'
            )
            self.assertEqual(resp.status_code, 400)
            data = json.loads(resp.content.decode())
            self.assertIn('error', data)

        user.refresh_from_db(using='team_northcliff')
        # 負になっていないことを再確認
        self.assertGreaterEqual(user.points, 0)
        self.assertEqual(user.points, 0)