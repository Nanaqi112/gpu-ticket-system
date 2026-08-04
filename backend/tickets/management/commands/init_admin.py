from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = '初始化管理员账号'

    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin2026'
        email = 'admin@example.com'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'管理员账号 {username} 已存在'))
            return

        User.objects.create_superuser(
            username=username,
            password=password,
            email=email
        )
        self.stdout.write(self.style.SUCCESS(f'管理员账号创建成功: {username}'))