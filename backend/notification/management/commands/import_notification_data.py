from django.core.management.base import BaseCommand
from django.core import serializers
from django.db import transaction
from notification.models import NotificationType, NotificationTemplate
import json
import os
from datetime import datetime


class Command(BaseCommand):
    help = '导入通知类型和模板数据，用于服务器同步'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--input-dir',
            type=str,
            help='包含导出文件的目录路径'
        )
        parser.add_argument(
            '--input-file',
            type=str,
            help='完整数据文件路径（JSON格式）'
        )
        parser.add_argument(
            '--types-file',
            type=str,
            help='通知类型文件路径'
        )
        parser.add_argument(
            '--templates-file',
            type=str,
            help='通知模板文件路径'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'fixture'],
            default='json',
            help='导入格式：json（自定义格式）或 fixture（Django fixture格式）'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='试运行模式，不实际写入数据库'
        )
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='强制更新已存在的数据'
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force_update = options['force_update']
        import_format = options['format']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 试运行模式：将显示导入预览，不会实际修改数据库')
            )
        
        try:
            if options['input_file']:
                # 导入完整数据文件
                self._import_complete_file(options['input_file'], dry_run, force_update)
            elif options['input_dir']:
                # 从目录导入最新文件
                self._import_from_directory(options['input_dir'], import_format, dry_run, force_update)
            elif options['types_file'] or options['templates_file']:
                # 分别导入类型和模板文件
                self._import_separate_files(
                    options['types_file'], 
                    options['templates_file'], 
                    import_format, 
                    dry_run, 
                    force_update
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ 请指定导入文件或目录')
                )
                return
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 导入失败: {str(e)}')
            )
            raise
    
    def _import_complete_file(self, filepath, dry_run, force_update):
        """导入完整数据文件"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f'文件不存在: {filepath}')
        
        self.stdout.write(f'📁 读取完整数据文件: {filepath}')
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查数据格式
        if 'notification_types' not in data or 'notification_templates' not in data:
            raise ValueError('数据文件格式错误，缺少必要字段')
        
        types_data = data['notification_types']
        templates_data = data['notification_templates']
        
        self.stdout.write(
            f'📊 数据统计: {len(types_data)} 个通知类型, {len(templates_data)} 个通知模板'
        )
        
        if not dry_run:
            with transaction.atomic():
                self._import_types_data(types_data, force_update)
                self._import_templates_data(templates_data, force_update)
        else:
            self._preview_import(types_data, templates_data)
    
    def _import_from_directory(self, directory, import_format, dry_run, force_update):
        """从目录导入最新的导出文件"""
        if not os.path.exists(directory):
            raise FileNotFoundError(f'目录不存在: {directory}')
        
        # 查找最新的导出文件
        if import_format == 'fixture':
            types_files = [f for f in os.listdir(directory) if f.startswith('notification_types_') and f.endswith('.json')]
            templates_files = [f for f in os.listdir(directory) if f.startswith('notification_templates_') and f.endswith('.json')]
        else:
            # 优先查找完整数据文件
            complete_files = [f for f in os.listdir(directory) if f.startswith('notification_data_complete_') and f.endswith('.json')]
            if complete_files:
                latest_file = max(complete_files)
                filepath = os.path.join(directory, latest_file)
                self._import_complete_file(filepath, dry_run, force_update)
                return
            
            types_files = [f for f in os.listdir(directory) if f.startswith('notification_types_') and f.endswith('.json')]
            templates_files = [f for f in os.listdir(directory) if f.startswith('notification_templates_') and f.endswith('.json')]
        
        if not types_files:
            raise FileNotFoundError(f'在目录 {directory} 中未找到通知类型文件')
        
        if not templates_files:
            raise FileNotFoundError(f'在目录 {directory} 中未找到通知模板文件')
        
        # 选择最新文件
        latest_types_file = max(types_files)
        latest_templates_file = max(templates_files)
        
        types_filepath = os.path.join(directory, latest_types_file)
        templates_filepath = os.path.join(directory, latest_templates_file)
        
        self._import_separate_files(types_filepath, templates_filepath, import_format, dry_run, force_update)
    
    def _import_separate_files(self, types_file, templates_file, import_format, dry_run, force_update):
        """分别导入类型和模板文件"""
        if import_format == 'fixture':
            self._import_fixture_files(types_file, templates_file, dry_run)
        else:
            self._import_json_files(types_file, templates_file, dry_run, force_update)
    
    def _import_fixture_files(self, types_file, templates_file, dry_run):
        """导入Django fixture格式文件"""
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 试运行模式不支持fixture格式预览，请使用实际导入')
            )
            return
        
        # 导入通知类型
        if types_file and os.path.exists(types_file):
            self.stdout.write(f'📁 导入通知类型: {types_file}')
            with open(types_file, 'r', encoding='utf-8') as f:
                for obj in serializers.deserialize('json', f):
                    obj.save()
            self.stdout.write(
                self.style.SUCCESS('✅ 通知类型导入完成')
            )
        
        # 导入通知模板
        if templates_file and os.path.exists(templates_file):
            self.stdout.write(f'📁 导入通知模板: {templates_file}')
            with open(templates_file, 'r', encoding='utf-8') as f:
                for obj in serializers.deserialize('json', f):
                    obj.save()
            self.stdout.write(
                self.style.SUCCESS('✅ 通知模板导入完成')
            )
    
    def _import_json_files(self, types_file, templates_file, dry_run, force_update):
        """导入自定义JSON格式文件"""
        types_data = []
        templates_data = []
        
        # 读取通知类型数据
        if types_file and os.path.exists(types_file):
            self.stdout.write(f'📁 读取通知类型文件: {types_file}')
            with open(types_file, 'r', encoding='utf-8') as f:
                types_data = json.load(f)
        
        # 读取通知模板数据
        if templates_file and os.path.exists(templates_file):
            self.stdout.write(f'📁 读取通知模板文件: {templates_file}')
            with open(templates_file, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)
        
        self.stdout.write(
            f'📊 数据统计: {len(types_data)} 个通知类型, {len(templates_data)} 个通知模板'
        )
        
        if not dry_run:
            with transaction.atomic():
                self._import_types_data(types_data, force_update)
                self._import_templates_data(templates_data, force_update)
        else:
            self._preview_import(types_data, templates_data)
    
    def _import_types_data(self, types_data, force_update):
        """导入通知类型数据"""
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for type_info in types_data:
            code = type_info['code']
            
            try:
                notification_type = NotificationType.objects.get(code=code)
                if force_update:
                    # 更新现有记录
                    notification_type.name = type_info['name']
                    notification_type.category = type_info['category']
                    notification_type.description = type_info['description']
                    notification_type.default_template = type_info['default_template']
                    notification_type.is_active = type_info['is_active']
                    notification_type.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'🔄 更新通知类型: {notification_type.name}')
                    )
                else:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'⏭️  跳过已存在的通知类型: {notification_type.name}')
                    )
            except NotificationType.DoesNotExist:
                # 创建新记录
                notification_type = NotificationType.objects.create(
                    code=code,
                    name=type_info['name'],
                    category=type_info['category'],
                    description=type_info['description'],
                    default_template=type_info['default_template'],
                    is_active=type_info['is_active']
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ 创建通知类型: {notification_type.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'📈 通知类型导入完成: 创建 {created_count} 个, 更新 {updated_count} 个, 跳过 {skipped_count} 个'
            )
        )
    
    def _import_templates_data(self, templates_data, force_update):
        """导入通知模板数据"""
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for template_info in templates_data:
            type_code = template_info['notification_type_code']
            
            try:
                notification_type = NotificationType.objects.get(code=type_code)
                
                try:
                    template = NotificationTemplate.objects.get(notification_type=notification_type)
                    if force_update:
                        # 更新现有模板
                        template.title_template = template_info['title_template']
                        template.content_template = template_info['content_template']
                        template.variables = template_info['variables']
                        template.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'🔄 更新通知模板: {notification_type.name}')
                        )
                    else:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'⏭️  跳过已存在的通知模板: {notification_type.name}')
                        )
                except NotificationTemplate.DoesNotExist:
                    # 创建新模板
                    template = NotificationTemplate.objects.create(
                        notification_type=notification_type,
                        title_template=template_info['title_template'],
                        content_template=template_info['content_template'],
                        variables=template_info['variables']
                    )
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ 创建通知模板: {notification_type.name}')
                    )
            
            except NotificationType.DoesNotExist:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'❌ 通知类型不存在: {type_code}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'📈 通知模板导入完成: 创建 {created_count} 个, 更新 {updated_count} 个, 跳过 {skipped_count} 个, 错误 {error_count} 个'
            )
        )
    
    def _preview_import(self, types_data, templates_data):
        """预览导入数据"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.WARNING('🔍 导入预览（试运行模式）')
        )
        self.stdout.write('='*60)
        
        # 预览通知类型
        self.stdout.write('\n📋 通知类型预览:')
        for i, type_info in enumerate(types_data[:5], 1):  # 只显示前5个
            code = type_info['code']
            name = type_info['name']
            category = type_info['category']
            
            try:
                existing = NotificationType.objects.get(code=code)
                status = '🔄 将更新' if existing else '⏭️  将跳过'
            except NotificationType.DoesNotExist:
                status = '✅ 将创建'
            
            self.stdout.write(f'  {i}. {name} ({code}) - {category} - {status}')
        
        if len(types_data) > 5:
            self.stdout.write(f'  ... 还有 {len(types_data) - 5} 个通知类型')
        
        # 预览通知模板
        self.stdout.write('\n📋 通知模板预览:')
        for i, template_info in enumerate(templates_data[:5], 1):  # 只显示前5个
            type_code = template_info['notification_type_code']
            title = template_info['title_template']
            
            try:
                notification_type = NotificationType.objects.get(code=type_code)
                try:
                    existing = NotificationTemplate.objects.get(notification_type=notification_type)
                    status = '🔄 将更新' if existing else '⏭️  将跳过'
                except NotificationTemplate.DoesNotExist:
                    status = '✅ 将创建'
            except NotificationType.DoesNotExist:
                status = '❌ 类型不存在'
            
            self.stdout.write(f'  {i}. {title} ({type_code}) - {status}')
        
        if len(templates_data) > 5:
            self.stdout.write(f'  ... 还有 {len(templates_data) - 5} 个通知模板')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.WARNING('💡 这是预览模式，没有实际修改数据库。\n   要执行实际导入，请移除 --dry-run 参数。')
        )
        self.stdout.write('='*60)