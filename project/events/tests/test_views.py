from types import NoneType

from authentication.models import User
from django.db.models.query import QuerySet
from django.urls import reverse
from events.models import (
    Event,
    RequestToParticipation,
)
from freezegun import freeze_time
from notifications.models import Notification
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from .set_up import SetUpEventsViews


class TestEventsViews(SetUpEventsViews):
    @freeze_time("2022-9-29")
    def test_event_create(self) -> None:
        self.create_events(1)
        self.assertEqual(Event.objects.first().status, "Planned")
        self.assertEqual(Event.objects.first().author.id, User.objects.first().id)

    @freeze_time("2022-9-29")
    def test_event_create_without_phone(self) -> None:
        self.auth()
        response = self.client.post(
            reverse("event-create"), self.event_create_withount_phone_data
        )
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(
            Event.objects.first().contact_number, User.objects.first().phone
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    @freeze_time("2022-9-29")
    def test_event_create_author_invites_himself(self) -> None:
        self.auth()
        self.event_create_data["current_users"].append(User.objects.first().id)
        response = self.client.post(reverse("event-create"), self.event_create_data)
        self.assertEqual(Notification.objects.count(), 0)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    @freeze_time("2022-10-01")
    def test_event_create_with_bad_start_time(self) -> None:
        self.auth()
        response = self.client.post(reverse("event-create"), self.event_create_data)
        self.assertEqual(Event.objects.count(), 0)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    @freeze_time("2022-9-29")
    def test_author_event_join(self) -> None:
        self.auth()
        self.client.post(reverse("event-create"), self.event_create_data)
        response = self.client.post(reverse("join-to-event"), self.event_join_data)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    @freeze_time("2022-9-29")
    def test_event_join(self) -> None:
        self.create_events(1)
        self.client.force_authenticate(None)
        self.client.post(reverse("register"), self.user_reg_data_2)
        self.client.force_authenticate(
            User.objects.get(email=self.user_reg_data_2["email"])
        )
        response = self.client.post(
            reverse("join-to-event"), {"event_id": Event.objects.first().id}
        )
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(Event.objects.first().count_current_users, 1)

    @freeze_time("2022-9-29")
    def test_second_event_join(self) -> None:
        self.create_events(1)
        self.register_second_user()
        event_join = self.client.post(
            reverse("join-to-event"), {"event_id": Event.objects.first().id}
        )
        event_join_2 = self.client.post(
            reverse("join-to-event"), {"event_id": Event.objects.first().id}
        )
        self.assertEqual(event_join.status_code, HTTP_200_OK)
        self.assertEqual(event_join_2.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(Event.objects.first().count_current_users, 1)

    @freeze_time("2022-9-29")
    def test_event_fan_join_to_event(self) -> None:
        self.create_events(1)
        self.register_second_user()
        fan_join_to_event = self.client.post(
            reverse("spectator-join-to-event"), {"event_id": Event.objects.first().id}
        )
        event_join = self.client.post(
            reverse("join-to-event"), {"event_id": Event.objects.first().id}
        )
        self.assertEqual(fan_join_to_event.status_code, HTTP_200_OK)
        self.assertEqual(event_join.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(Event.objects.first().count_current_fans, 1)
        self.assertEqual(Event.objects.first().count_current_users, 0)

    @freeze_time("2022-9-29")
    def test_leave_from_event(self) -> None:
        self.create_events(1)
        self.register_second_user()
        event_join = self.client.post(
            reverse("join-to-event"), {"event_id": Event.objects.first().id}
        )
        self.assertEqual(Event.objects.first().count_current_users, 1)
        event_leave = self.client.post(
            reverse("leave-from-event"), {"event_id": Event.objects.first().id}
        )
        self.assertEqual(Notification.objects.count(), 2)
        self.assertEqual(Event.objects.first().count_current_users, 0)
        self.assertEqual(event_join.status_code, HTTP_200_OK)
        self.assertEqual(event_leave.status_code, HTTP_200_OK)

    @freeze_time("2022-9-29")
    def test_no_event_participant_leave_from_event(self) -> None:
        self.create_events(1)
        self.register_second_user()
        event_leave = self.client.post(
            reverse("leave-from-event"), {"event_id": Event.objects.first().id}
        )
        self.assertEqual(Notification.objects.count(), 0)
        self.assertEqual(event_leave.status_code, HTTP_400_BAD_REQUEST)

    @freeze_time("2022-9-29")
    def test_user_events_list(self) -> None:
        self.create_events(10)
        get_user_events_list = self.client.get(reverse("user-events-list"))
        self.client.force_authenticate(None)
        self.client.post(reverse("register"), self.user_reg_data_2)
        self.client.force_authenticate(
            User.objects.get(email=self.user_reg_data_2["email"])
        )
        get_user_events_list_2 = self.client.get(reverse("user-events-list"))
        self.assertEqual(Event.objects.count(), 10)
        self.assertEqual(get_user_events_list.data["total_count"], 10)
        self.assertEqual(get_user_events_list.status_code, HTTP_200_OK)
        self.assertEqual(get_user_events_list_2.data["total_count"], 0)
        self.assertEqual(get_user_events_list_2.status_code, HTTP_200_OK)

    @freeze_time("2022-9-29")
    def test_bulk_delete_events(self) -> None:
        self.create_events(10)
        response = self.client.post(
            reverse("bulk-delete-events"),
            {"ids": [Event.objects.first().id, Event.objects.last().id]},
        )
        self.assertEqual(Event.objects.count(), 8)
        self.assertEqual(response.status_code, HTTP_200_OK)

    @freeze_time("2022-9-29")
    def test_no_author_bulk_delete_events(self) -> None:
        self.create_events(10)
        self.register_second_user()
        response = self.client.post(
            reverse("bulk-delete-events"),
            {"ids": [Event.objects.first().id, Event.objects.last().id]},
        )
        self.assertEqual(Event.objects.count(), 10)
        self.assertEqual(response.status_code, HTTP_200_OK)

    @freeze_time("2022-9-29")
    def test_update_event(self) -> None:
        self.create_events(1)
        get_event = self.client.get(
            reverse("get-event", kwargs={"pk": Event.objects.first().id})
        )
        response = self.client.put(
            reverse("update-event", kwargs={"pk": Event.objects.first().id}),
            self.event_update_data,
        )
        get_event_after_update = self.client.get(
            reverse("get-event", kwargs={"pk": Event.objects.first().id})
        )
        self.assertEqual(get_event.data["name"], self.event_create_data["name"])
        self.assertTrue(
            get_event_after_update.data["name"] != self.event_create_data["name"]
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

    @freeze_time("2022-9-29")
    def test_no_author_update_event(self) -> None:
        self.create_events(1)
        self.register_second_user()
        response = self.client.put(
            reverse("update-event", kwargs={"pk": Event.objects.first().id}),
            self.event_update_data,
        )
        get_event = self.client.get(
            reverse("get-event", kwargs={"pk": Event.objects.first().id})
        )
        self.assertTrue(get_event.data["name"] != self.event_update_data["name"])
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    @freeze_time("2022-9-29")
    def test_invite_user_to_event(self) -> None:
        self.create_events(1)
        self.client.force_authenticate(None)
        self.client.post(reverse("register"), self.user_reg_data_2)
        self.auth()
        self.assertEqual(Notification.objects.count(), 0)
        response = self.client.post(
            reverse("invite-to-event"),
            {
                "user_id": User.objects.get(email=self.user_reg_data_2["email"]).id,
                "event_id": Event.objects.first().id,
            },
        )
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(
            Notification.objects.first().user.email, self.user_reg_data_2["email"]
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

    @freeze_time("2022-9-29")
    def test_author_invites_himself(self) -> None:
        self.create_events(1)
        self.assertEqual(Notification.objects.count(), 0)
        response = self.client.post(
            reverse("invite-to-event"),
            {"user_id": User.objects.first().id, "event_id": Event.objects.first().id},
        )
        self.assertEqual(Notification.objects.count(), 0)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    @freeze_time("2022-9-29")
    def test_invite_event_author_to_his_event(self) -> None:
        self.create_events(1)
        self.register_second_user()
        response = self.client.post(
            reverse("invite-to-event"),
            {
                "user_id": Event.objects.first().author.id,
                "event_id": Event.objects.first().id,
            },
        )
        self.assertEqual(Notification.objects.count(), 0)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    @freeze_time("2022-9-29")
    def test_invite_user_who_is_already_participating_in_this_event(self) -> None:
        self.create_events(1)
        self.register_second_user()
        event_join = self.client.post(
            reverse("join-to-event"), {"event_id": Event.objects.first().id}
        )
        self.client.force_authenticate(None)
        self.auth()
        response = self.client.post(
            reverse("invite-to-event"),
            {
                "user_id": Event.objects.first().current_users.first().id,
                "event_id": Event.objects.first().id,
            },
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(event_join.status_code, HTTP_200_OK)

    @freeze_time("2022-9-29")
    def test_user_send_request_to_participation(self) -> None:
        self.auth()
        self.event_create_data["privacy"] = True
        event_create = self.client.post(reverse("event-create"), self.event_create_data)
        self.assertEqual(event_create.status_code, HTTP_201_CREATED)
        self.register_second_user()
        event_join = self.client.post(
            reverse("join-to-event"), {"event_id": Event.objects.first().id}
        )
        self.assertEqual(Event.objects.first().count_current_users, 0)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(RequestToParticipation.objects.count(), 1)
        self.assertEqual(event_join.status_code, HTTP_200_OK)

    @freeze_time("2022-9-29")
    def test_event_author_send_request_to_participation(self) -> None:
        self.auth()
        self.event_create_data["privacy"] = True
        event_create = self.client.post(reverse("event-create"), self.event_create_data)
        self.assertEqual(event_create.status_code, HTTP_201_CREATED)
        event_join = self.client.post(
            reverse("join-to-event"), {"event_id": Event.objects.first().id}
        )
        self.assertEqual(Event.objects.first().count_current_users, 0)
        self.assertEqual(Notification.objects.count(), 0)
        self.assertEqual(RequestToParticipation.objects.count(), 0)
        self.assertEqual(event_join.status_code, HTTP_400_BAD_REQUEST)

    # @freeze_time('2022-9-29')
    # def test_get_user_planned_events(self) -> None:
    #     self.auth()
    #     self.create_events(10)
    #     get_event = self.client.get(reverse('user-planned-events-list', kwargs = {'pk': Event.objects.first().author.id}))
    #     print(get_event.data)
    #     self.assertEqual(get_event.status_code, HTTP_200_OK)

    @freeze_time("2022-9-29")
    def test_accept_request_to_participation(self) -> None:
        self.auth()
        self.event_create_data["privacy"] = True
        event_create = self.client.post(reverse("event-create"), self.event_create_data)
        self.register_second_user()
        event_join = self.client.post(
            reverse("join-to-event"), {"event_id": Event.objects.first().id}
        )
        self.client.force_authenticate(None)
        self.auth()
        accept_request_to_participation = self.client.post(
            reverse("accept-decline-participations"),
            {"ids": [RequestToParticipation.objects.first().id], "type": True},
        )
        self.assertEqual(Event.objects.first().count_current_users, 1)
        self.assertEqual(event_join.status_code, HTTP_200_OK)

    @freeze_time("2022-9-29")
    def create_events(self, count: int) -> QuerySet[Event]:
        self.auth()
        for create_event in range(count):
            event_create = self.client.post(
                reverse("event-create"), self.event_create_data
            )
            self.assertEqual(event_create.status_code, HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), count)
        return Event.objects.all()

    def register_second_user(self) -> NoneType:
        self.client.force_authenticate(None)
        register = self.client.post(reverse("register"), self.user_reg_data_2)
        self.assertEqual(register.status_code, HTTP_201_CREATED)
        return self.client.force_authenticate(
            User.objects.get(email=self.user_reg_data_2["email"])
        )

    def auth(self) -> NoneType:
        self.client.post(reverse("register"), self.user_reg_data)
        user = User.objects.get(email=self.user_reg_data["email"])
        return self.client.force_authenticate(user)
