from django.core.management.base import BaseCommand
from organization.signals import ensure_organization_verification_notification_setup


class Command(BaseCommand):
    help = '初始化组织认证通知类型和模板（包括认证通过和认证被拒绝）'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始初始化组织认证通知...'))
        
        try:
            result = ensure_organization_verification_notification_setup()
            
            if result and all(result):
                success_type, rejected_type, success_template, rejected_template = result
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ 成功初始化组织认证通知系统：\n'
                        f'   - 认证通过通知类型：{success_type.name} (分类: {success_type.category})\n'
                        f'   - 认证通过通知模板：{success_template.title_template}\n'
                        f'   - 认证被拒绝通知类型：{rejected_type.name} (分类: {rejected_type.category})\n'
                        f'   - 认证被拒绝通知模板：{rejected_template.title_template}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ 初始化失败：数据库连接问题或其他错误，请检查数据库配置')
                )
                return
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 初始化失败：{str(e)}')
            )
            return
        
        self.stdout.write(self.style.SUCCESS('🎉 组织认证通知系统初始化完成！'))