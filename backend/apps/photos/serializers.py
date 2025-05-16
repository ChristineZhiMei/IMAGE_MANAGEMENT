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