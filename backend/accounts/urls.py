from django.urls import path

from .support_views import SupportChatView, SupportMembersView, SupportPendingPaymentsView, SupportRoomListView, SupportStaffChatView
from .views import LoginView, MembershipInfoView, MeView, ProfileView, RegisterView, UpgradePlanView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("membership/", MembershipInfoView.as_view(), name="membership"),
    path("upgrade/", UpgradePlanView.as_view(), name="upgrade"),
    path("upgrade/<int:pk>/", UpgradePlanView.as_view(), name="upgrade-delete"),
    path("support/chat/", SupportChatView.as_view(), name="support-chat"),
    path("support/payments/", SupportPendingPaymentsView.as_view(), name="support-payments"),
    path("support/rooms/", SupportRoomListView.as_view(), name="support-rooms"),
    path("support/rooms/<int:room_id>/", SupportStaffChatView.as_view(), name="support-room-chat"),
    path("support/members/", SupportMembersView.as_view(), name="support-members"),
]
