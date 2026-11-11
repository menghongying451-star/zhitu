from django.urls import path

from .views import AgentChatView, AgentListView, AgentMetaView, ConversationDetailView, ConversationListView

urlpatterns = [
    path("", AgentListView.as_view(), name="agent_list"),
    # 放在 <name>/ 前面，避免 "conversations" 被当成智能体名
    path("conversations/", ConversationListView.as_view(), name="agent_conversations"),
    path("conversations/<str:conv_id>/", ConversationDetailView.as_view(), name="agent_conversation_detail"),
    path("<str:name>/", AgentMetaView.as_view(), name="agent_meta"),
    path("<str:name>/chat/", AgentChatView.as_view(), name="agent_chat"),
]
