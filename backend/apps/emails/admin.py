from django.contrib import admin

from apps.emails.models import Email


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipient_email',
        'subject',
        'status',
        'sent_at',
    )

    search_fields = (
        'recipient_email',
        'subject',
    )

    list_filter = (
        'status',
    )