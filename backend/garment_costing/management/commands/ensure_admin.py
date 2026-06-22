from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = "确保存在一个超级管理员账号"

    def handle(self, *args, **options):
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username="admin",
                password="suanjiabao2026",
                display_name="管理员",
            )
            self.stdout.write(self.style.SUCCESS("已创建超级管理员: admin / suanjiabao2026"))
        else:
            self.stdout.write("超级管理员已存在，跳过")
