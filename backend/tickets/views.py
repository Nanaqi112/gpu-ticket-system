from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Ticket, Attachment
from .serializers import (
    TicketListSerializer,
    TicketDetailSerializer,
    TicketCreateSerializer,
    TicketUpdateSerializer,
    AttachmentSerializer
)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketListSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TicketUpdateSerializer
        elif self.action == 'retrieve':
            return TicketDetailSerializer
        return TicketListSerializer

    def get_queryset(self):
        queryset = Ticket.objects.all()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(serial_number__icontains=search) |
                Q(source__icontains=search) |
                Q(fault_description__icontains=search)
            )

        return queryset

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取工单统计数据"""
        total = Ticket.objects.count()
        completed = Ticket.objects.filter(status='completed').count()
        in_progress = Ticket.objects.filter(status='in_progress').count()

        return Response({
            'total': total,
            'completed': completed,
            'in_progress': in_progress,
        })

    @action(detail=True, methods=['delete'])
    def delete_attachment(self, request, pk=None):
        """删除指定附件"""
        ticket = self.get_object()
        attachment_id = request.data.get('attachment_id')

        try:
            attachment = ticket.attachments.get(id=attachment_id)
            attachment.file.delete()
            attachment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Attachment.DoesNotExist:
            return Response(
                {'error': '附件不存在'},
                status=status.HTTP_404_NOT_FOUND
            )