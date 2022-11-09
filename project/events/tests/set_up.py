from collections import OrderedDict

from rest_framework.test import APITestCase


class SetUpEventsViews(APITestCase):
    def setUp(self) -> OrderedDict:
        self.event_create_data = {
            "name": "string",
            "description": "string",
            "place": "string",
            "gender": "Man",
            "date_and_time": "2022-9-30T10:44:32.275Z",
            "contact_number": "+380683861202",
            "need_ball": True,
            "amount_members": 50,
            "type": "Football",
            "price": 32767,
            "price_description": "string",
            "need_form": True,
            "privacy": False,
            "duration": 10,
            "forms": "Shirt-Front",
            "current_users": [],
        }

        self.event_create_withount_phone_data = {
            "name": "string",
            "description": "string",
            "place": "string",
            "gender": "Man",
            "date_and_time": "2022-9-30T10:44:32.275Z",
            "need_ball": True,
            "amount_members": 50,
            "type": "Football",
            "price": 32767,
            "price_description": "string",
            "need_form": True,
            "privacy": False,
            "duration": 10,
            "forms": "Shirt-Front",
            "current_users": [],
        }

        self.event_update_data = {
            "name": "updated",
            "description": "string",
            "place": "string",
            "gender": "Man",
            "date_and_time": "2022-9-30T10:44:32.275Z",
            "contact_number": "+380683861202",
            "need_ball": True,
            "amount_members": 50,
            "type": "Football",
            "price": 32767,
            "price_description": "string",
            "need_form": True,
            "privacy": False,
            "duration": 10,
            "forms": "Shirt-Front",
        }

        self.event_join_data = {"event_id": 1}

        self.user_reg_data = {
            "email": "user@example.com",
            "phone": "+380683861969",
            "password": "string11",
            "re_password": "string11",
            "profile": {
                "name": "string",
                "last_name": "string",
                "gender": "Man",
                "birthday": "2000-09-10",
                "height": 30,
                "weight": 30,
                "position": "ST",
                "about_me": "string",
            },
        }

        self.user_reg_data_2 = {
            "email": "user@example.com2",
            "phone": "+380683861980",
            "password": "string11",
            "re_password": "string11",
            "profile": {
                "name": "string",
                "last_name": "string",
                "gender": "Man",
                "birthday": "2000-09-10",
                "height": 30,
                "weight": 30,
                "position": "ST",
                "about_me": "string",
            },
        }
        self.fan_event_join_data = {"event_id": 0}
