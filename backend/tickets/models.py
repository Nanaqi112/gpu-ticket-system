from django.db import models
from django.utils import timezone


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('in_progress', '进行中'),
        ('completed', '已完成'),
    ]

    MODEL_CHOICES = [
        ('H100', 'H100'),
        ('H200', 'H200'),
        ('B200', 'B200'),
        ('A100', 'A100'),
        ('A800', 'A800'),
        ('L40S', 'L40S'),
        ('OTHER', '其他'),
    ]

    model_type = models.CharField(max_length=20, choices=MODEL_CHOICES, verbose_name='型号类别')
    serial_number = models.CharField(max_length=100, unique=True, db_index=True, verbose_name='序列号')
    source = models.CharField(max_length=200, verbose_name='来源地')
    fault_description = models.TextField(verbose_name='故障描述')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress', db_index=True, verbose_name='状态')
    created_at = models.DateTimeField(db_index=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(verbose_name='更新时间')

    class Meta:
        verbose_name = '工单'
        verbose_name_plural = '工单'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.serial_number} - {self.get_model_type_display()}"

    @property
    def days_elapsed(self):
        """计算从更新时间到现在经过的天数"""
        delta = timezone.now() - self.updated_at
        return delta.days


class Attachment(models.Model):
    FILE_TYPE_CHOICES = [
        ('image', '图片'),
        ('document', '文档'),
        ('log', '日志'),
        ('other', '其他'),
    ]

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments', verbose_name='所属工单')
    file = models.FileField(upload_to='tickets/%Y/%m/', verbose_name='文件')
    file_name = models.CharField(max_length=255, verbose_name='文件名')
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, verbose_name='文件类型')
    file_size = models.IntegerField(default=0, verbose_name='文件大小')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')

    class Meta:
        verbose_name = '附件'
        verbose_name_plural = '附件'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.file_name

    @property
    def url(self):
        if self.file:
            return self.file.url
        return None