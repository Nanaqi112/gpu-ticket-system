import io

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from .models import Ticket, Attachment
from .permissions import IsAdminOrReadOnly
from .authentication import CsrfExemptSessionAuthentication
from .serializers import (
    TicketListSerializer,
    TicketDetailSerializer,
    TicketCreateSerializer,
    TicketUpdateSerializer,
    AttachmentSerializer
)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([CsrfExemptSessionAuthentication])
def login_view(request):
    """用户登录"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': '请输入用户名和密码'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({
            'id': user.id,
            'username': user.username,
            'is_staff': user.is_staff,
        })
    else:
        return Response(
            {'error': '用户名或密码错误'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CsrfExemptSessionAuthentication])
def logout_view(request):
    """用户登出"""
    logout(request)
    return Response({'message': '已登出'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    """获取当前用户信息"""
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'is_staff': user.is_staff,
    })


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketListSerializer
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

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

    @action(detail=False, methods=['get'])
    def export(self, request):
        """导出全部工单数据为 Excel"""
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = '工单数据'

        headers = ['序列号', '型号', '来源地', '故障描述', '状态', '创建时间', '更新时间', '已过天数', '附件数']
        sheet.append(headers)

        header_fill = PatternFill('solid', fgColor='4472C4')
        for cell in sheet[1]:
            cell.font = Font(bold=True, color='FFFFFF')
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', vertical='center')

        tickets = Ticket.objects.annotate(attachment_count=Count('attachments'))
        for ticket in tickets:
            sheet.append([
                ticket.serial_number,
                ticket.get_model_type_display(),
                ticket.source,
                ticket.fault_description,
                ticket.get_status_display(),
                ticket.created_at.strftime('%Y-%m-%d'),
                ticket.updated_at.strftime('%Y-%m-%d'),
                ticket.days_elapsed,
                ticket.attachment_count,
            ])

        for row in sheet.iter_rows(min_row=2):
            row[3].alignment = Alignment(wrap_text=True, vertical='top')

        column_widths = [22, 12, 20, 50, 12, 14, 14, 10, 10]
        for index, width in enumerate(column_widths, start=1):
            sheet.column_dimensions[get_column_letter(index)].width = width
        sheet.freeze_panes = 'A2'

        buffer = io.BytesIO()
        workbook.save(buffer)

        filename = f"tickets_{timezone.localtime().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

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