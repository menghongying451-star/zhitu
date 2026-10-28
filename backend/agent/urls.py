from django.urls import path

from .views import AgentChatView, AgentListView, AgentMetaView

urlpatterns = [
    path("", AgentListView.as_view(), name="agent_list"),
    path("<str:name>/", AgentMetaView.as_view(), name="agent_meta"),
    path("<str:name>/chat/", AgentChatView.as_view(), name="agent_chat"),
]
