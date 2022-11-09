from typing import Union

from django.urls import path
from django.urls.resolvers import (
    URLPattern,
    URLResolver,
)
from events.views import (
    BulkAcceptOrDeclineInvitesToEvent,
    BulkAcceptOrDeclineRequestToParticipation,
    CreateEvent,
    DeleteEvents,
    EventsList,
    EventsRelevantList,
    FanJoinToEvent,
    FanLeaveFromEvent,
    GetEvent,
    InvitesToEventList,
    InviteUserToEvent,
    JoinToEvent,
    LeaveFromEvent,
    PopularEvents,
    RemoveUserFromEvent,
    RequestToParticipationsList,
    UpdateEvent,
    UserEventsList,
    UserEventsRelevantList,
    UserParticipantEventsList,
    UserPlannedEventsList,
)

urlpatterns: list[Union[URLResolver, URLPattern]] = [
    # endpoint where user can create new event
    path("client/event/create", CreateEvent.as_view(), name="event-create"),
    # endpoint where user can get event
    path("client/event/<int:pk>", GetEvent.as_view(), name="get-event"),
    # endpoint where user can update event
    path("client/event/update/<int:pk>", UpdateEvent.as_view(), name="update-event"),
    # endpoint where user can get list of events
    path("client/events/list", EventsList.as_view(), name="events-list"),
    # endpoint where user can get list of events
    path(
        "client/invites/to/events/list",
        InvitesToEventList.as_view(),
        name="invites-to-events-list",
    ),
    # endpoint where user can bulk delete events
    path("client/events/delete", DeleteEvents.as_view(), name="bulk-delete-events"),
    # endpoint where user can join to event
    path("client/event/join", JoinToEvent.as_view(), name="join-to-event"),
    # endpoint where user can remove player from his event
    path(
        "client/remove/user/from/event",
        RemoveUserFromEvent.as_view(),
        name="remove-user-from-event",
    ),
    # endpoint where user can leave from event
    path("client/event/leave", LeaveFromEvent.as_view(), name="leave-from-event"),
    # endpoint where user can join to event like a spectator
    path(
        "client/fan/event/join",
        FanJoinToEvent.as_view(),
        name="spectator-join-to-event",
    ),
    # endpoint where spectator can leave from event
    path(
        "client/fan/event/leave",
        FanLeaveFromEvent.as_view(),
        name="spectator-leave-from-event",
    ),
    # endpoint where user can get list of your events
    path("client/my/events/list", UserEventsList.as_view(), name="user-events-list"),
    # endpoint where user can get list of your events
    path(
        "client/my/participant/events/list",
        UserParticipantEventsList.as_view(),
        name="user-participant-events-list",
    ),
    # endpoint where user can get relevant list of events
    path(
        "client/relevant/events/list",
        EventsRelevantList.as_view(),
        name="relevant-event-list",
    ),
    # endpoint where user can get relevant list of events
    path(
        "client/my/relevant/events/list",
        UserEventsRelevantList.as_view(),
        name="relevant-user-events-list",
    ),
    # endpoint where a user can get list of other user scheduled events
    path(
        "client/user/planned/events/list/<int:pk>",
        UserPlannedEventsList.as_view(),
        name="user-planned-events-list",
    ),
    # endpoint where a user can get list of the most popular events
    path(
        "client/popular/events/list",
        PopularEvents.as_view(),
        name="popular-events-list",
    ),
    # endpoint where a user can invite other user to ivent
    path(
        "client/invite/user/to/event",
        InviteUserToEvent.as_view(),
        name="invite-to-event",
    ),
    # endpoint where user can get list of your requests-participations
    path(
        "client/requests/participations/list<int:pk>",
        RequestToParticipationsList.as_view(),
        name="request-participations-list",
    ),
    #
    path(
        "client/accept/or/decline/participations",
        BulkAcceptOrDeclineRequestToParticipation.as_view(),
        name="accept-decline-participations",
    ),
    path(
        "client/accept/or/decline/invites/to/events",
        BulkAcceptOrDeclineInvitesToEvent.as_view(),
        name="accept-decline-invites-to-event",
    ),
]
