from django.contrib import admin

from .models import ChatConversation, ChatMessage


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("role", "content", "actions", "created_at")
    can_delete = False


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ("title", "agent", "user", "created_at", "updated_at")
    list_filter = ("agent",)
    search_fields = ("title", "user__username")
    readonly_fields = ("id", "user", "agent", "inputs", "created_at", "updated_at")
    inlines = [ChatMessageInline]
