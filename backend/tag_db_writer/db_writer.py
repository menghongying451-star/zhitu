from django.db import transaction
from django.utils import timezone
from user.models import Tag1, Tag2, Tag1StuMatch, Tag2StuMatch, Student
from project.models import Requirement

# 模型映射配置
MODEL_MAPPING = {
    "tag1_student": {
        "model": Tag1StuMatch,
        "primary_key_field": "student",
        "tag_field": "tag1",
        "primary_model": Student,
        "tag_model": Tag1,
    },
    "tag2_student": {
        "model": Tag2StuMatch,
        "primary_key_field": "student",
        "tag_field": "tag2",
        "primary_model": Student,
        "tag_model": Tag2,
    },
    "tag1_requirement": {
        "model": Requirement,
        "primary_key_field": "id",
        "tag_field": "tag1",
        "primary_model": Requirement,
        "tag_model": Tag1,
        "is_many_to_many": True,
    },
    "tag2_requirement": {
        "model": Requirement,
        "primary_key_field": "id",
        "tag_field": "tag2",
        "primary_model": Requirement,
        "tag_model": Tag2,
        "is_many_to_many": True,
    },
}


def insert_match_from_json(input_json: dict):
    """
    使用Django ORM处理标签匹配数据插入
    
    输入格式:
    {
      "match_type": "tag1_student",
      "data": [
        {"student_id": 1, "tag1_id": [3, 5, 7]},
        {"student_id": 2, "tag1_id": 4}
      ]
    }
    """
    
    match_type = input_json.get("match_type")
    data_list = input_json.get("data", [])
    
    if match_type not in MODEL_MAPPING:
        raise ValueError(f"未知匹配类型: {match_type}")
    
    config = MODEL_MAPPING[match_type]
    model = config["model"]
    primary_key_field = config["primary_key_field"]
    tag_field = config["tag_field"]
    primary_model = config["primary_model"]
    tag_model = config["tag_model"]
    is_many_to_many = config.get("is_many_to_many", False)
    
    # 使用数据库事务确保数据一致性
    with transaction.atomic():
        for idx, item in enumerate(data_list):
            print(f"处理第{idx+1}条数据：{item}")
            
            # 验证必要字段
            primary_key_name = f"{primary_key_field}_id" if primary_key_field != "id" else "id"
            if match_type.endswith("_student"):
                primary_key_name = "student_id"
            elif match_type.endswith("_requirement"):
                primary_key_name = "requirement_id"
                
            tag_field_name = f"{tag_field}_id"
            
            if primary_key_name not in item or tag_field_name not in item:
                raise ValueError(f"缺少必要字段：{primary_key_name} 或 {tag_field_name}")
            
            primary_key_value = item[primary_key_name]
            if isinstance(primary_key_value, list):
                raise ValueError(f"{primary_key_name} 字段不能是列表，只能是单个值: {primary_key_value}")
            
            tag_ids = item[tag_field_name]
            if not isinstance(tag_ids, list):
                tag_ids = [tag_ids]
            
            # 验证主键对象是否存在
            try:
                if match_type.endswith("_student"):
                    primary_obj = Student.objects.get(id=primary_key_value)
                elif match_type.endswith("_requirement"):
                    primary_obj = Requirement.objects.get(id=primary_key_value)
            except (Student.DoesNotExist, Requirement.DoesNotExist):
                raise ValueError(f"主键对象不存在: {primary_key_name}={primary_key_value}")
            
            # 验证标签对象是否存在
            existing_tags = tag_model.objects.filter(id__in=tag_ids)
            existing_tag_ids = set(existing_tags.values_list('id', flat=True))
            invalid_tag_ids = set(tag_ids) - existing_tag_ids
            if invalid_tag_ids:
                raise ValueError(f"标签不存在: {invalid_tag_ids}")
            
            if is_many_to_many:
                # 处理多对多关系（项目标签）
                tag_relation = getattr(primary_obj, tag_field)
                # 清除现有关系
                tag_relation.clear()
                # 添加新关系
                tag_relation.set(tag_ids)
            else:
                # 处理一对多关系（学生标签）
                # 删除现有关系
                filter_kwargs = {primary_key_field: primary_obj}
                model.objects.filter(**filter_kwargs).delete()
                
                # 批量创建新关系
                new_matches = []
                for tag_id in tag_ids:
                    tag_obj = tag_model.objects.get(id=tag_id)
                    match_kwargs = {
                        primary_key_field: primary_obj,
                        tag_field: tag_obj,
                        'created_at': timezone.now()
                    }
                    new_matches.append(model(**match_kwargs))
                
                # 批量插入
                if new_matches:
                    model.objects.bulk_create(new_matches)


# 保持向后兼容的函数名
def insert_general_match(match_type, data_list):
    """
    向后兼容的函数，转换为新的输入格式
    """
    input_json = {
        "match_type": match_type,
        "data": data_list
    }
    return insert_match_from_json(input_json)