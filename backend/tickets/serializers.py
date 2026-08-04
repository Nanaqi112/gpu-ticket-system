from rest_framework import serializers
from .models import Ticket, Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField()

    class Meta:
        model = Attachment
        fields = ['id', 'file', 'file_name', 'file_type', 'file_size', 'uploaded_at', 'url']
        read_only_fields = ['id', 'uploaded_at', 'url']


class TicketListSerializer(serializers.ModelSerializer):
    days_elapsed = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    model_display = serializers.CharField(source='get_model_type_display', read_only=True)
    attachment_count = serializers.IntegerField(source='attachments.count', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'model_type', 'model_display', 'serial_number', 'source',
            'status', 'status_display', 'created_at', 'updated_at',
            'days_elapsed', 'attachment_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'days_elapsed']


class TicketDetailSerializer(serializers.ModelSerializer):
    days_elapsed = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    model_display = serializers.CharField(source='get_model_type_display', read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'model_type', 'model_display', 'serial_number', 'source',
            'fault_description', 'status', 'status_display', 'created_at',
            'updated_at', 'days_elapsed', 'attachments'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'days_elapsed']


class TicketCreateSerializer(serializers.ModelSerializer):
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Ticket
        fields = [
            'model_type', 'serial_number', 'source', 'fault_description', 'created_at', 'updated_at', 'attachments'
        ]

    def validate_serial_number(self, value):
        if Ticket.objects.filter(serial_number=value).exists():
            raise serializers.ValidationError("该序列号已存在")
        return value

    def validate_attachments(self, files):
        from django.conf import settings
        for f in files:
            if f.size > 10 * 1024 * 1024:  # 10MB per file
                raise serializers.ValidationError(f"文件 {f.name} 超过10MB限制")
        return files

    def create(self, validated_data):
        attachments_data = validated_data.pop('attachments', [])
        ticket = Ticket.objects.create(**validated_data)

        for file in attachments_data:
            file_type = 'other'
            if file.content_type.startswith('image/'):
                file_type = 'image'
            elif file.content_type in ['application/pdf', 'text/plain', 'text/csv']:
                file_type = 'document'
            elif file.name.endswith(('.log', '.txt')):
                file_type = 'log'

            Attachment.objects.create(
                ticket=ticket,
                file=file,
                file_name=file.name,
                file_type=file_type,
                file_size=file.size
            )

        return ticket


class TicketUpdateSerializer(serializers.ModelSerializer):
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Ticket
        fields = ['model_type', 'serial_number', 'source', 'fault_description', 'status', 'updated_at', 'attachments']

    def update(self, instance, validated_data):
        attachments_data = validated_data.pop('attachments', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for file in attachments_data:
            file_type = 'other'
            if file.content_type.startswith('image/'):
                file_type = 'image'
            elif file.content_type in ['application/pdf', 'text/plain', 'text/csv']:
                file_type = 'document'
            elif file.name.endswith(('.log', '.txt')):
                file_type = 'log'

            Attachment.objects.create(
                ticket=instance,
                file=file,
                file_name=file.name,
                file_type=file_type,
                file_size=file.size
            )

        return instance