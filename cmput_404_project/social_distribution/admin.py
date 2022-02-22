from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import AuthorCreationForm, AuthorChangeForm
from .models import Author


class AuthorAdmin(UserAdmin):
    add_form = AuthorCreationForm
    form = AuthorChangeForm
    model = Author
    list_display = ('username', 'github', 'is_staff', 'is_active')
    list_filter = ('username', 'github', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'github', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )
    search_fields = ('username',)
    ordering = ('username',)


admin.site.register(Author, AuthorAdmin)
