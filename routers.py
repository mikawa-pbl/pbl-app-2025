# routers.py （プロジェクト直下）
class TeamPerAppRouter:
    """
    team_a アプリは team_a DB、team_b アプリは team_b DB へルーティングする。
    それ以外は default。
    """

    app_to_db = {
        'team_USL': 'team_USL',
        'team_kitajaki': 'team_kitajaki',
        'agileca': 'agileca',
        'team_scim': 'team_scim',
        'team_empiricism': 'team_empiricism', # 追加
        'ssk': 'ssk',
        'team_tansaibou': 'team_tansaibou',
        'shiokara': 'shiokara',
        'mori_doragon_yuhi_machi': 'mori_doragon_yuhi_machi',
        'team_northcliff': 'team_northcliff',
        "team_TMR": "team_TMR",  # ← 追加
        "graphics": "graphics",
        "team_terrace": "team_terrace",
        "team_UD": "team_UD",
        "nanakorobiyaoki": "nanakorobiyaoki",
        "team_akb5": "team_akb5",
        "team_TeXTeX": "team_TeXTeX",
        "team_cake": "team_cake",
        "team_shouronpou": "team_shouronpou",
        'Catan': 'Catan',
        'takenoko': 'takenoko',
        "h34vvy_u53rzz": "h34vvy_u53rzz",
        'team_giryulink': 'team_giryulink',
    }

    def db_for_read(self, model, **hints):
        return self.app_to_db.get(model._meta.app_label, "default")

    def db_for_write(self, model, **hints):
        return self.app_to_db.get(model._meta.app_label, "default")

    def allow_relation(self, obj1, obj2, **hints):
        # 同じDB(=同じチーム)間なら許可。違うDB間のFK等は基本NG運用推奨。
        db1 = self.app_to_db.get(obj1._meta.app_label, "default")
        db2 = self.app_to_db.get(obj2._meta.app_label, "default")
        return db1 == db2

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # 各アプリのマイグレーションは、そのアプリ専用DBにのみ適用
        target_db = self.app_to_db.get(app_label)
        if target_db:
            return db == target_db
        # チーム外(app_labelが team_a / team_b 以外)は default へ
        return db == "default"
