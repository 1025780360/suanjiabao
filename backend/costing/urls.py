from django.urls import path

from .views import AiChatHistoryView, CostingChatView, QuickCategoryDeleteView, QuickCategoryListCreateView, QuickStyleDeleteView, QuickStyleListCreateView

urlpatterns = [
    path("quick-categories/", QuickCategoryListCreateView.as_view(), name="quick-categories"),
    path("quick-categories/<slug:key>/", QuickCategoryDeleteView.as_view(), name="quick-category-delete"),
    path("quick-styles/", QuickStyleListCreateView.as_view(), name="quick-styles"),
    path("quick-styles/<int:pk>/", QuickStyleDeleteView.as_view(), name="quick-style-delete"),
    path("ai/costing-chat/", CostingChatView.as_view(), name="costing-chat"),
    path("ai/chat-history/", AiChatHistoryView.as_view(), name="chat-history"),
]
