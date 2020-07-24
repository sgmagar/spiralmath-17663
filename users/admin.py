from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from users.forms import UserChangeForm, UserCreationForm
from users.models import UserType

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (("User", {"fields": ("status",)}),) + auth_admin.UserAdmin.fieldsets
    list_display = ["username", "first_name", "is_superuser"]
    search_fields = ["username"]


@admin.register(UserType)
class UserType(admin.ModelAdmin):
    """Simple admin for UserType."""

    list_display = ('id', 'name', 'create_questions', 'review_questions', 'created', 'modified')
    list_filter = ('id',)
