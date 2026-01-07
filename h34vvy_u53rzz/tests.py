import json
from django.test import TestCase
from django.urls import reverse

from .models import User, Facility, FacilityAccess


class FailTest(TestCase):
    """テストが失敗したときにCIが異常終了することを確認するテスト"""
    databases = {'h34vvy_u53rzz'}

    def test_always_fail(self):
        self.assertEqual(1, 2)
