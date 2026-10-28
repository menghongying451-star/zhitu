#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Django 迁移文件清理脚本

此脚本用于从Git版本控制中移除不必要的迁移文件，
只保留 __init__.py 和 0001_initial.py 文件。

使用方法：
1. 确保你在项目根目录
2. 运行: python cleanup_migrations.py
3. 检查输出并确认要移除的文件
4. 如果确认无误，运行: python cleanup_migrations.py --execute
"""

import os
import subprocess
import sys
import re
from pathlib import Path

def find_migration_files():
    """查找所有需要从Git中移除的迁移文件"""
    try:
        # 获取所有被Git跟踪的迁移文件
        result = subprocess.run(
            ['git', 'ls-files'],
            capture_output=True,
            text=True,
            check=True
        )
        
        all_files = result.stdout.strip().split('\n')
        migration_files = [f for f in all_files if '/migrations/' in f and f.endswith('.py')]
        
        # 过滤出需要移除的文件（保留 __init__.py 和 0001_initial.py）
        files_to_remove = []
        files_to_keep = []
        
        for file in migration_files:
            filename = os.path.basename(file)
            if filename == '__init__.py' or filename == '0001_initial.py':
                files_to_keep.append(file)
            elif re.match(r'^\d{4}_.*\.py$', filename):
                files_to_remove.append(file)
            else:
                files_to_keep.append(file)  # 其他文件也保留
        
        return files_to_remove, files_to_keep
    
    except subprocess.CalledProcessError as e:
        print(f"错误：无法执行git命令: {e}")
        return [], []
    except Exception as e:
        print(f"错误：{e}")
        return [], []

def remove_files_from_git(files_to_remove, execute=False):
    """从Git中移除文件"""
    if not files_to_remove:
        print("没有需要移除的迁移文件。")
        return True
    
    print(f"\n将要从Git中移除以下 {len(files_to_remove)} 个迁移文件：")
    for file in files_to_remove:
        print(f"  - {file}")
    
    if not execute:
        print("\n这是预览模式。如果要实际执行，请运行：")
        print("python cleanup_migrations.py --execute")
        return True
    
    try:
        # 从Git中移除文件（但保留本地文件）
        cmd = ['git', 'rm', '--cached'] + files_to_remove
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print(f"\n成功从Git中移除了 {len(files_to_remove)} 个迁移文件。")
        print("\n接下来你需要：")
        print("1. 提交这些更改：")
        print("   git commit -m 'Remove migration files from version control'")
        print("\n2. 推送到远程仓库：")
        print("   git push")
        
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"错误：无法从Git中移除文件: {e}")
        if e.stderr:
            print(f"错误详情: {e.stderr}")
        return False

def check_git_status():
    """检查Git状态"""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.stdout.strip():
            print("警告：工作目录有未提交的更改：")
            print(result.stdout)
            response = input("是否继续？(y/N): ")
            if response.lower() != 'y':
                return False
        
        return True
    
    except subprocess.CalledProcessError:
        print("错误：无法检查Git状态。请确保你在Git仓库中。")
        return False

def main():
    """主函数"""
    print("Django 迁移文件清理工具")
    print("=" * 40)
    
    # 检查是否在Git仓库中
    if not os.path.exists('.git'):
        print("错误：当前目录不是Git仓库。")
        sys.exit(1)
    
    # 检查是否有 --execute 参数
    execute = '--execute' in sys.argv
    
    if execute:
        print("执行模式：将实际移除文件")
        if not check_git_status():
            sys.exit(1)
    else:
        print("预览模式：只显示将要移除的文件")
    
    # 查找迁移文件
    files_to_remove, files_to_keep = find_migration_files()
    
    print(f"\n找到 {len(files_to_keep)} 个将保留的迁移文件：")
    for file in files_to_keep:
        print(f"  ✓ {file}")
    
    # 移除文件
    success = remove_files_from_git(files_to_remove, execute)
    
    if not success:
        sys.exit(1)
    
    if execute:
        print("\n清理完成！")
        print("\n建议接下来的步骤：")
        print("1. 检查 .gitignore 文件是否包含迁移文件规则")
        print("2. 在团队中分享 DJANGO_MIGRATIONS_GUIDE.md 文档")
        print("3. 确保所有开发者了解新的迁移文件管理流程")

if __name__ == '__main__':
    main()