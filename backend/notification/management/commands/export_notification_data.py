from django.core.management.base import BaseCommand
from django.core import serializers
from notification.models import NotificationType, NotificationTemplate
import json
import os
from datetime import datetime


class Command(BaseCommand):
    help = '导出通知类型和模板数据到JSON文件，用于服务器同步'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='notification_data_export',
            help='导出文件的目录路径（默认：notification_data_export）'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'fixture'],
            default='json',
            help='导出格式：json（自定义格式）或 fixture（Django fixture格式）'
        )
    
    def handle(self, *args, **options):
        output_dir = options['output_dir']
        export_format = options['format']
        
        # 创建导出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.stdout.write(f'创建导出目录: {output_dir}')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if export_format == 'fixture':
            self._export_as_fixture(output_dir, timestamp)
        else:
            self._export_as_json(output_dir, timestamp)
    
    def _export_as_fixture(self, output_dir, timestamp):
        """导出为Django fixture格式"""
        # 导出通知类型
        notification_types = NotificationType.objects.all()
        types_filename = f'notification_types_{timestamp}.json'
        types_filepath = os.path.join(output_dir, types_filename)
        
        with open(types_filepath, 'w', encoding='utf-8') as f:
            serializers.serialize('json', notification_types, indent=2, stream=f, ensure_ascii=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ 导出 {notification_types.count()} 个通知类型到: {types_filepath}')
        )
        
        # 导出通知模板
        notification_templates = NotificationTemplate.objects.all()
        templates_filename = f'notification_templates_{timestamp}.json'
        templates_filepath = os.path.join(output_dir, templates_filename)
        
        with open(templates_filepath, 'w', encoding='utf-8') as f:
            serializers.serialize('json', notification_templates, indent=2, stream=f, ensure_ascii=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ 导出 {notification_templates.count()} 个通知模板到: {templates_filepath}')
        )
        
        # 创建导入说明文件
        readme_content = f"""# 通知数据导入说明

## 文件说明
- `{types_filename}`: 通知类型数据（Django fixture格式）
- `{templates_filename}`: 通知模板数据（Django fixture格式）

## 导入方法

### 方法1：使用Django loaddata命令
```bash
# 导入通知类型
python manage.py loaddata {types_filename}

# 导入通知模板
python manage.py loaddata {templates_filename}
```

### 方法2：使用自定义导入命令
```bash
python manage.py import_notification_data --input-dir {output_dir}
```

## 注意事项
1. 导入前请确保目标数据库已运行迁移：`python manage.py migrate`
2. 如果数据已存在，Django会跳过重复数据
3. 建议在导入前备份目标数据库
4. 导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        readme_filepath = os.path.join(output_dir, 'README.md')
        with open(readme_filepath, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ 创建导入说明文件: {readme_filepath}')
        )
    
    def _export_as_json(self, output_dir, timestamp):
        """导出为自定义JSON格式"""
        # 导出通知类型
        notification_types = NotificationType.objects.all()
        types_data = []
        
        for nt in notification_types:
            types_data.append({
                'code': nt.code,
                'name': nt.name,
                'category': nt.category,
                'description': nt.description,
                'default_template': nt.default_template,
                'is_active': nt.is_active,
            })
        
        types_filename = f'notification_types_{timestamp}.json'
        types_filepath = os.path.join(output_dir, types_filename)
        
        with open(types_filepath, 'w', encoding='utf-8') as f:
            json.dump(types_data, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ 导出 {len(types_data)} 个通知类型到: {types_filepath}')
        )
        
        # 导出通知模板
        notification_templates = NotificationTemplate.objects.select_related('notification_type').all()
        templates_data = []
        
        for nt in notification_templates:
            templates_data.append({
                'notification_type_code': nt.notification_type.code,
                'title_template': nt.title_template,
                'content_template': nt.content_template,
                'variables': nt.variables,
            })
        
        templates_filename = f'notification_templates_{timestamp}.json'
        templates_filepath = os.path.join(output_dir, templates_filename)
        
        with open(templates_filepath, 'w', encoding='utf-8') as f:
            json.dump(templates_data, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ 导出 {len(templates_data)} 个通知模板到: {templates_filepath}')
        )
        
        # 创建合并数据文件
        combined_data = {
            'notification_types': types_data,
            'notification_templates': templates_data,
            'export_info': {
                'timestamp': datetime.now().isoformat(),
                'total_types': len(types_data),
                'total_templates': len(templates_data)
            }
        }
        
        combined_filename = f'notification_data_complete_{timestamp}.json'
        combined_filepath = os.path.join(output_dir, combined_filename)
        
        with open(combined_filepath, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ 创建合并数据文件: {combined_filepath}')
        )
        
        # 创建导入说明文件
        readme_content = f"""# 通知数据导入说明

## 文件说明
- `{types_filename}`: 通知类型数据（自定义JSON格式）
- `{templates_filename}`: 通知模板数据（自定义JSON格式）
- `{combined_filename}`: 完整数据文件（包含类型和模板）

## 导入方法

### 使用自定义导入命令
```bash
# 导入完整数据
python manage.py import_notification_data --input-file {combined_filename}

# 或分别导入
python manage.py import_notification_data --types-file {types_filename} --templates-file {templates_filename}
```

## 数据统计
- 通知类型数量：{len(types_data)}
- 通知模板数量：{len(templates_data)}
- 导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 注意事项
1. 导入前请确保目标数据库已运行迁移：`python manage.py migrate`
2. 导入时会自动处理重复数据（基于code字段）
3. 建议在导入前备份目标数据库
"""
        
        readme_filepath = os.path.join(output_dir, 'README.md')
        with open(readme_filepath, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ 创建导入说明文件: {readme_filepath}')
        )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 数据导出完成！\n'
                f'导出目录：{output_dir}\n'
                f'通知类型：{len(types_data)} 个\n'
                f'通知模板：{len(templates_data)} 个'
            )
        )
        self.stdout.write('='*60)