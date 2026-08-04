from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = '初始化用户账号'

    def handle(self, *args, **options):
        # 创建管理员账号
        admin_username = 'admin'
        admin_password = 'admin2026'

        if User.objects.filter(username=admin_username).exists():
            self.stdout.write(self.style.WARNING(f'管理员账号 {admin_username} 已存在'))
        else:
            User.objects.create_superuser(
                username=admin_username,
                password=admin_password,
                email='admin@example.com'
            )
            self.stdout.write(self.style.SUCCESS(f'管理员账号创建成功: {admin_username}'))

        # 创建普通用户账号
        test_username = 'test'
        test_password = 'test'

        if User.objects.filter(username=test_username).exists():
            self.stdout.write(self.style.WARNING(f'普通用户 {test_username} 已存在'))
        else:
            User.objects.create_user(
                username=test_username,
                password=test_password,
                email='test@example.com',
                is_staff=False
            )
            self.stdout.write(self.style.SUCCESS(f'普通用户创建成功: {test_username}'))