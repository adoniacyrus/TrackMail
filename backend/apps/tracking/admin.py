from django.contrib import admin

from apps.tracking.models import EmailOpenEvent


@admin.register(EmailOpenEvent)
class EmailOpenEventAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'ip_address',
        'opened_at',
    )

    search_fields = (
        'email__subject',
        'ip_address',
    )

    list_filter = (
        'opened_at',
    )