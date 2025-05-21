# -*- coding: utf-8 -*-
"""
序列化器
序列化器是将数据转换为特定格式的过程，通常用于网络传输或存储。
序列化器可以将数据转换为 JSON、XML 或其他格式，以便在不同的系统之间进行传输。
"""

from rest_framework import serializers
import time
# noinspection PyUnresolvedReferences
from config import ConfigController

# noinspection PyUnresolvedReferences
from apps.photos.utils import return_format_suffix
# noinspection PyUnresolvedReferences
from apps.photos.utils_set.get_time import get_format

# 设置默认信息对象
configSG = ConfigController()

class DefaultInfo(object):
    def __init__(
            self,
    ):
        self.setting_path = {
            "readPath": configSG.get_setting()[0],
            "cachePath": configSG.get_setting()[1]
        }
        self.classify_labels = configSG.get_classify()
        self.supportFileFormats = return_format_suffix()
        self.supportDateFormats = get_format()
        if self.setting_path['readPath'] == '':
            self.status = 0
            self.description = '请设置图片读取路径'
        else:
            self.status = 1
            self.description = '获取成功'
        self.timestamp = time.time()

# 序列化默认对象
class DefaultSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    setting_path = serializers.DictField(child=serializers.CharField())
    classify_labels = serializers.ListField(child=serializers.CharField())
    description = serializers.CharField(allow_blank=True)
    timestamp = serializers.FloatField()
    supportFileFormats = serializers.ListField(child=serializers.CharField())
    supportDateFormats = serializers.ListField(child=serializers.CharField())

# 设置路径对象
class SettingPath(object):
    def __init__(
            self,
            read_path:str,
            cache_path:str,
    ):
        self.read_path = read_path
        self.cache_path = cache_path
# 序列化设置路径对象
class SettingPathSerializer(serializers.Serializer):
    read_path = serializers.CharField()
    cache_path = serializers.CharField()

# 设置基本返回格式
class BasicResponse(object):
    def __init__(
            self,
            status:int,
            operation:str,
            failedPath: list[dict[str,str]],
            totalNum:int,
            successNum:int,
            failedNum:int,
            description:str,
    ):
        self.status = status
        self.operation = operation
        self.failedPath = failedPath
        self.totalNum = totalNum
        self.successNum = successNum
        self.failedNum = failedNum
        self.description = description
        self.timestamp = time.time()
# 序列化基本返回格式对象
class BasicResponseSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    operation = serializers.CharField()
    failedPath = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    totalNum = serializers.IntegerField()
    successNum = serializers.IntegerField()
    failedNum = serializers.IntegerField()
    description = serializers.CharField(allow_blank=True)
    timestamp = serializers.FloatField()

class EditExifResponse(object):
    def __init__(self,status:int,description:str,camera_info:dict,photo_info:dict):
        self.status = status
        self.description = description
        self.camera_info = camera_info
        self.photo_info = photo_info
        self.timestamp = time.time()
class EditExifResponseSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    description = serializers.CharField(allow_blank=True)
    camera_info = serializers.DictField(
        child=serializers.CharField()
    )
    photo_info = serializers.DictField(
        child=serializers.CharField()
    )
    timestamp = serializers.FloatField()

# 返回日期序列化
class PhotoNodeSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    date_type = serializers.CharField()

class DayNodeSerializer(PhotoNodeSerializer):
    def to_representation(self, instance):
        # 处理日期节点下的照片数据
        if not isinstance(instance, dict):
            return {}
        photo_data = instance.get('02', {})
        return PhotoNodeSerializer(photo_data).data

class MonthNodeSerializer(PhotoNodeSerializer):
    days = serializers.SerializerMethodField()

    def get_days(self, instance):
        if not isinstance(instance, dict):
            return {}
        days_data = {}
        for day_key, day_data in instance.items():
            if isinstance(day_data, dict) and day_data.get('date_type') == 'days':
                days_data[day_key] = day_data
        return DayNodeSerializer(days_data, many=False).data

class YearNodeSerializer(PhotoNodeSerializer):
    months = serializers.SerializerMethodField()

    def get_months(self, instance):
        if not isinstance(instance, dict):
            return {}
        months_data = {}
        for month_key, month_data in instance.items():
            if isinstance(month_data, dict) and month_data.get('date_type') == 'months':
                months_data[month_key] = month_data
        return MonthNodeSerializer(months_data, many=False).data

class DateStructureSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    description = serializers.CharField(allow_blank=True)
    total_photo = serializers.IntegerField()
    timestamp = serializers.FloatField(required=False, allow_null=True)
    date = YearNodeSerializer(required=False, allow_null=True)

    def to_representation(self, instance):
        # 处理date字段为空的情况
        ret = super().to_representation(instance)
        if 'date' not in instance or instance['date'] is None:
            ret['date'] = None
        return ret