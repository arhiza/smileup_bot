from django.contrib import admin

# Register your models here.
from .models import Post, BotUser

def make_moderated(modeladmin, request, queryset):
    queryset.update(status=Post.OK)
make_moderated.short_description = "Mark selected quotes as published"

class PostAdmin(admin.ModelAdmin):
    list_display = ["status", "quote", "link", "nick_id"] #
    ordering = ["status"]
    actions = [make_moderated]

admin.site.register(Post, PostAdmin)


class BotUserAdmin(admin.ModelAdmin):
    list_display = ["nick_name", "nick_id", "dialog", "sent_message", "next_message", "need_link", "user_min", "user_max"]

admin.site.register(BotUser, BotUserAdmin)

