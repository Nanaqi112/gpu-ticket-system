from django.contrib import admin
from .models import Ticket, Attachment


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ['file_name', 'file_type', 'file_size', 'uploaded_at']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['serial_number', 'model_type', 'source', 'status', 'created_at', 'days_elapsed']
    list_filter = ['status', 'model_type', 'created_at']
    search_fields = ['serial_number', 'source', 'fault_description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [AttachmentInline]

    def days_elapsed(self, obj):
        return obj.days_elapsed
    days_elapsed.short_description = '已过天数'


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'ticket', 'file_type', 'file_size', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['file_name']