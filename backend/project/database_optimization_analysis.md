# 数据库索引优化与缓存策略分析

## 概述

本文档基于当前系统的查询模式，分析资源和需求管理相关接口的性能瓶颈，提出数据库索引优化方案和缓存策略设计。

## 当前查询模式分析

### 1. 需求列表查询 (`list_requirements`)

#### 主要查询条件
- **状态筛选**: `status` 字段过滤
- **组织筛选**: `organization_id` 字段过滤
- **时间范围筛选**: `created_at` 字段范围查询
- **预算筛选**: `budget` 字段模糊匹配和范围查询
- **关键词搜索**: `title`, `description`, `tag1`, `tag2` 多字段模糊查询
- **排序操作**: `title`, `created_at`, `views` 字段排序

#### 关联查询
```python
queryset = Requirement.objects.select_related(
    'organization', 'publish_people__user'
).prefetch_related(
    'tag1', 'tag2', 'resources', 'files'
)
```

### 2. 资源列表查询 (`list_resources`)

#### 主要查询条件
- **状态筛选**: `status` 字段过滤
- **组织筛选**: `create_person__organization_id` 字段过滤
- **时间范围筛选**: `created_at` 字段范围查询
- **关键词搜索**: `title`, `tag1`, `tag2` 多字段模糊查询
- **排序操作**: `title`, `created_at`, `downloads`, `views` 字段排序

#### 关联查询
```python
queryset = Resource.objects.select_related(
    'create_person__user', 'update_person__user'
).prefetch_related(
    'tag1', 'tag2', 'files'
)
```

### 3. 资源统计查询 (`get_resource_statistics`)

#### 主要查询条件
- **时间范围筛选**: `created_at` 字段范围查询（当前和上期对比）
- **组织筛选**: `create_person__organization_id` 字段过滤
- **状态统计**: `status` 字段分组统计
- **聚合计算**: `downloads`, `views` 字段求和
- **热门数据**: `downloads`, `views` 字段排序取前N条
- **标签统计**: 通过多对多关系统计标签使用频次

## 索引优化方案

### 1. Requirement 模型索引优化

#### 当前索引状态
```python
class Meta:
    ordering = ['-created_at']  # 默认排序，Django会自动创建索引
```

#### 建议新增索引
```python
class Meta:
    verbose_name = '需求'
    verbose_name_plural = '需求'
    ordering = ['-created_at']
    indexes = [
        # 单字段索引
        models.Index(fields=['status'], name='req_status_idx'),
        models.Index(fields=['organization'], name='req_org_idx'),
        models.Index(fields=['created_at'], name='req_created_idx'),
        models.Index(fields=['views'], name='req_views_idx'),
        models.Index(fields=['title'], name='req_title_idx'),
        
        # 复合索引（按查询频率排序）
        models.Index(fields=['status', 'created_at'], name='req_status_created_idx'),
        models.Index(fields=['organization', 'status'], name='req_org_status_idx'),
        models.Index(fields=['organization', 'created_at'], name='req_org_created_idx'),
        models.Index(fields=['status', 'organization', 'created_at'], name='req_status_org_created_idx'),
        
        # 排序优化索引
        models.Index(fields=['-views'], name='req_views_desc_idx'),
        models.Index(fields=['-created_at'], name='req_created_desc_idx'),
    ]
```

### 2. Resource 模型索引优化

#### 当前索引状态
```python
class Meta:
    ordering = ['-created_at']  # 默认排序，Django会自动创建索引
```

#### 建议新增索引
```python
class Meta:
    verbose_name = '资源'
    verbose_name_plural = '资源'
    ordering = ['-created_at']
    indexes = [
        # 单字段索引
        models.Index(fields=['status'], name='res_status_idx'),
        models.Index(fields=['type'], name='res_type_idx'),
        models.Index(fields=['create_person'], name='res_creator_idx'),
        models.Index(fields=['created_at'], name='res_created_idx'),
        models.Index(fields=['title'], name='res_title_idx'),
        
        # 数值字段索引（注意：当前是CharField，建议改为IntegerField）
        models.Index(fields=['downloads'], name='res_downloads_idx'),
        models.Index(fields=['views'], name='res_views_idx'),
        
        # 复合索引
        models.Index(fields=['status', 'created_at'], name='res_status_created_idx'),
        models.Index(fields=['create_person', 'status'], name='res_creator_status_idx'),
        models.Index(fields=['create_person', 'created_at'], name='res_creator_created_idx'),
        
        # 组织相关复合索引（通过create_person关联）
        # 注意：这需要在查询时使用create_person__organization_id
        
        # 排序优化索引
        models.Index(fields=['-downloads'], name='res_downloads_desc_idx'),
        models.Index(fields=['-views'], name='res_views_desc_idx'),
        models.Index(fields=['-created_at'], name='res_created_desc_idx'),
        
        # 统计查询优化索引
        models.Index(fields=['status', 'created_at', 'downloads'], name='res_stat_idx'),
        models.Index(fields=['status', 'created_at', 'views'], name='res_stat_views_idx'),
    ]
```

### 3. 多对多关系表索引优化

#### Tag1 和 Tag2 关联表
```python
# Django会自动为多对多关系创建中间表，但我们可以优化查询
# 在Tag1和Tag2模型中添加索引

# Tag1模型优化
class Tag1(models.Model):
    # ... 现有字段
    class Meta:
        db_table = 'tag_1'
        verbose_name = '兴趣标签'
        verbose_name_plural = '兴趣标签'
        indexes = [
            models.Index(fields=['value'], name='tag1_value_idx'),
            # 为全文搜索优化
            models.Index(fields=['value'], name='tag1_value_text_idx', 
                        opclasses=['varchar_pattern_ops']),
        ]

# Tag2模型优化
class Tag2(models.Model):
    # ... 现有字段
    class Meta:
        db_table = 'tag_2'
        verbose_name = '能力标签'
        verbose_name_plural = '能力标签'
        indexes = [
            models.Index(fields=['category'], name='tag2_category_idx'),
            models.Index(fields=['subcategory'], name='tag2_subcategory_idx'),
            models.Index(fields=['specialty'], name='tag2_specialty_idx'),
            models.Index(fields=['parent'], name='tag2_parent_idx'),
            models.Index(fields=['level'], name='tag2_level_idx'),
            # 复合索引用于层级查询
            models.Index(fields=['category', 'subcategory'], name='tag2_cat_subcat_idx'),
            models.Index(fields=['category', 'subcategory', 'specialty'], name='tag2_full_path_idx'),
        ]
```

### 4. 关联模型索引优化

#### OrganizationUser 模型（已有部分索引）
```python
# 当前已有的索引很好，建议补充：
class Meta:
    indexes = [
        models.Index(fields=['permission'], name='org_user_perm_idx'),
        models.Index(fields=['status'], name='org_user_status_idx'),
        models.Index(fields=['organization'], name='org_user_org_idx'),
        # 新增复合索引
        models.Index(fields=['organization', 'permission'], name='org_user_org_perm_idx'),
        models.Index(fields=['organization', 'status'], name='org_user_org_status_idx'),
    ]
```

## 数据类型优化建议

### 1. 数值字段类型优化

当前Resource模型中的数值字段使用CharField，建议优化：

```python
class Resource(models.Model):
    # 当前定义
    downloads = models.CharField(max_length=255, default='0', verbose_name='下载数')
    views = models.CharField(max_length=255, default='0', verbose_name='浏览数')
    
    # 建议优化为
    downloads = models.PositiveIntegerField(default=0, verbose_name='下载数', db_index=True)
    views = models.PositiveIntegerField(default=0, verbose_name='浏览数', db_index=True)
```

**优化理由**：
1. 数值类型支持更高效的排序和聚合操作
2. 索引效率更高
3. 存储空间更小
4. 支持数据库级别的数值运算

### 2. 需求模型数值字段优化

```python
class Requirement(models.Model):
    # 当前定义
    views = models.IntegerField(default=0, verbose_name='浏览数')  # 已经是正确类型
    
    # 建议为views字段添加索引
    class Meta:
        indexes = [
            # ... 其他索引
            models.Index(fields=['views'], name='req_views_idx'),
        ]
```

## 缓存策略设计

### 1. 缓存需求分析

#### 高频查询场景
1. **资源/需求列表查询** - 分页数据，查询频繁
2. **资源统计数据** - 计算复杂，实时性要求不高
3. **热门标签/资源** - 变化频率低，访问频率高
4. **组织信息** - 变化频率极低，关联查询频繁

#### 缓存收益评估
- **高收益场景**：统计数据、热门排行、标签信息
- **中等收益场景**：列表查询（首页数据）
- **低收益场景**：详情页面（个性化程度高）

### 2. 缓存架构设计

#### 缓存层级
```
应用层缓存 (Django Cache Framework)
    ↓
Redis 缓存 (主要缓存存储)
    ↓
数据库查询 (最终数据源)
```

#### 缓存配置
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'zhihui_platform',
        'TIMEOUT': 300,  # 默认5分钟
    },
    'statistics': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'zhihui_stats',
        'TIMEOUT': 3600,  # 统计数据缓存1小时
    }
}
```

### 3. 具体缓存实现方案

#### 3.1 资源统计数据缓存

```python
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_resource_statistics(request):
    period = request.GET.get('period', 'week')
    date = request.GET.get('date')
    organization_id = request.GET.get('organization_id')
    
    # 构建缓存键
    cache_key = f"resource_stats_{period}_{date}_{organization_id or 'all'}"
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key, using='statistics')
    if cached_data:
        return APIResponse.success(cached_data, "获取资源统计成功（缓存）")
    
    # 缓存未命中，执行查询
    try:
        # ... 原有查询逻辑
        result_data = {
            'status_distribution': status_distribution,
            'data_statistics': data_statistics,
            'hot_tag1s': hot_tag1s,
            'hot_downloads': hot_downloads,
            'hot_views': hot_views
        }
        
        # 存入缓存，统计数据缓存30分钟
        cache.set(cache_key, result_data, timeout=1800, using='statistics')
        
        return APIResponse.success(result_data, "获取资源统计成功")
        
    except Exception as e:
        # ... 错误处理
```

#### 3.2 热门数据缓存

```python
def get_hot_resources_cached(limit=5, cache_timeout=3600):
    """获取热门资源（带缓存）"""
    cache_key = f"hot_resources_{limit}"
    
    hot_resources = cache.get(cache_key)
    if hot_resources is None:
        # 查询热门资源
        hot_resources = Resource.objects.filter(
            status='published'
        ).order_by('-downloads', '-views')[:limit]
        
        # 序列化数据
        serialized_data = ResourceSerializer(hot_resources, many=True).data
        
        # 缓存1小时
        cache.set(cache_key, serialized_data, timeout=cache_timeout)
        
        return serialized_data
    
    return hot_resources

def get_hot_tags_cached(limit=10, cache_timeout=3600):
    """获取热门标签（带缓存）"""
    cache_key = f"hot_tags_{limit}"
    
    hot_tags = cache.get(cache_key)
    if hot_tags is None:
        # 统计标签使用频次
        from django.db.models import Count
        
        hot_tags = Tag1.objects.annotate(
            usage_count=Count('resource') + Count('requirement')
        ).order_by('-usage_count')[:limit]
        
        # 序列化数据
        serialized_data = [{
            'tag': tag.value,
            'count': str(tag.usage_count)
        } for tag in hot_tags]
        
        # 缓存1小时
        cache.set(cache_key, serialized_data, timeout=cache_timeout)
        
        return serialized_data
    
    return hot_tags
```

#### 3.3 列表查询缓存（可选）

```python
# 对于首页或默认查询条件的列表，可以考虑短时间缓存
def get_default_resource_list_cached():
    """获取默认资源列表（首页）"""
    cache_key = "default_resource_list"
    
    cached_list = cache.get(cache_key)
    if cached_list is None:
        # 查询默认列表（前20条已发布资源）
        resources = Resource.objects.filter(
            status='published'
        ).select_related(
            'create_person__user'
        ).prefetch_related(
            'tag1', 'tag2'
        ).order_by('-created_at')[:20]
        
        serialized_data = ResourceSerializer(resources, many=True).data
        
        # 缓存5分钟（较短时间，保证数据新鲜度）
        cache.set(cache_key, serialized_data, timeout=300)
        
        return serialized_data
    
    return cached_list
```

### 4. 缓存失效策略

#### 4.1 主动失效

```python
# 在数据更新时主动清除相关缓存
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Resource)
def invalidate_resource_cache(sender, instance, **kwargs):
    """资源数据更新时清除相关缓存"""
    # 清除统计缓存
    cache_pattern = "resource_stats_*"
    cache.delete_pattern(cache_pattern, using='statistics')
    
    # 清除热门资源缓存
    cache.delete("hot_resources_5")
    cache.delete("default_resource_list")
    
    # 如果是状态变更，清除更多缓存
    if instance.status == 'published':
        cache.delete("hot_tags_10")

@receiver(post_delete, sender=Resource)
def invalidate_resource_cache_on_delete(sender, instance, **kwargs):
    """资源删除时清除缓存"""
    # 清除所有相关缓存
    cache_pattern = "resource_stats_*"
    cache.delete_pattern(cache_pattern, using='statistics')
    cache.delete("hot_resources_5")
    cache.delete("hot_tags_10")
    cache.delete("default_resource_list")
```

#### 4.2 定时失效

```python
# 使用Celery定时任务清理过期缓存
from celery import shared_task

@shared_task
def refresh_hot_data_cache():
    """定时刷新热门数据缓存"""
    # 预热热门资源缓存
    get_hot_resources_cached()
    
    # 预热热门标签缓存
    get_hot_tags_cached()
    
    return "Hot data cache refreshed"

# 在settings.py中配置定时任务
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'refresh-hot-data': {
        'task': 'project.tasks.refresh_hot_data_cache',
        'schedule': crontab(minute=0),  # 每小时执行一次
    },
}
```

## 性能监控建议

### 1. 数据库查询监控

```python
# 使用Django Debug Toolbar监控开发环境查询
# 生产环境使用django-silk或自定义中间件

class QueryCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.db import connection, reset_queries
        
        reset_queries()
        response = self.get_response(request)
        
        query_count = len(connection.queries)
        if query_count > 10:  # 查询数量阈值
            logger.warning(f"High query count: {query_count} for {request.path}")
        
        return response
```

### 2. 缓存命中率监控

```python
import logging
from django.core.cache import cache

cache_logger = logging.getLogger('cache')

def cache_get_with_logging(key, default=None, using='default'):
    """带日志的缓存获取"""
    value = cache.get(key, default, using=using)
    
    if value is not None:
        cache_logger.info(f"Cache HIT: {key}")
    else:
        cache_logger.info(f"Cache MISS: {key}")
    
    return value
```

## 实施建议

### 1. 分阶段实施

**第一阶段：索引优化**
1. 添加单字段索引
2. 优化数据类型（downloads, views字段）
3. 添加最关键的复合索引

**第二阶段：基础缓存**
1. 实施统计数据缓存
2. 实施热门数据缓存
3. 配置缓存失效机制

**第三阶段：高级优化**
1. 列表查询缓存
2. 查询优化和监控
3. 性能调优

### 2. 风险控制

1. **索引添加**：在低峰期执行，避免锁表
2. **数据类型变更**：需要数据迁移，建议分批执行
3. **缓存实施**：先在测试环境验证，逐步推广
4. **监控告警**：设置性能监控和告警机制

### 3. 预期效果

1. **查询性能提升**：列表查询响应时间减少50-70%
2. **统计查询优化**：复杂统计查询响应时间减少60-80%
3. **并发能力提升**：支持更高的并发访问量
4. **用户体验改善**：页面加载速度明显提升

## 总结

通过合理的索引设计和缓存策略，可以显著提升系统性能。建议优先实施索引优化，然后逐步引入缓存机制。在实施过程中要注意监控系统性能变化，及时调整优化策略。