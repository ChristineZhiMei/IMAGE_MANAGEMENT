import json
import time

from django.http import HttpResponse, JsonResponse
from django.views import View

# noinspection PyUnresolvedReferences
from apps.photos.serializers import DefaultInfo,DefaultSerializer,BasicResponse,BasicResponseSerializer
# noinspection PyUnresolvedReferences
from apps.photos.utils import delete_photos,move_photos
# noinspection PyUnresolvedReferences
from config import ConfigController

configSG = ConfigController()
# Create your views here.
# noinspection PyUnusedLocal
class PhotoMainView(View):
    # noinspection PyUnusedLocal
    def get(self, request):
        print("get请求")
        return HttpResponse("get请求")
    def post(self, request):
        print("post请求")
        return HttpResponse("post请求")
# 获取默认信息
class DefaultView(View):
    def get(self, request):
        info = DefaultInfo()
        serializer = DefaultSerializer(info)
        # print(serializer.data)
        return JsonResponse(serializer.data)

#设置路径
class SettingsView(View):
    def post(self, request):
        settings = json.loads(request.body)
        if settings['readPath'] == settings['cachePath']:
            response = {
                'status':0,
                'description':'读取路径和缓存路径不能相同',
                'timestamp':time.time()
            }
            return JsonResponse(response)
        logs = configSG.set_setting(settings['readPath'],settings['cachePath'])
        response = {
            'status':logs[0],
            'description':logs[1]+' | '+logs[2],
            'timestamp':time.time()
        }
        # print(response)
        return JsonResponse(response)
    def get(self, request):
        settings = configSG.get_setting()
        response = {
           'status':1,
            'readPath':settings[0],
            'cachePath':settings[1],
            'description':'获取成功'
        }
        return JsonResponse(response)
# 设置分类标签
class ClassifyView(View):
    def get(self, request):
        labels = configSG.get_classify()
        response = {
            'status':1,
            'classifyLabels':labels,
            'description':'获取成功',
            'timestamp':time.time(),
        }
        return JsonResponse(response)
    def post(self, request):
        labels = json.loads(request.body)['classifyLabels']
        logs = configSG.set_classify(labels)
        response = {
            'status':logs[0],
            'description':logs[1],
            'timestamp':time.time(),
        }
        return JsonResponse(response)

# 删除图片
class DeleteView(View):
    def post(self, request):
        filePaths = json.loads(request.body)['filePath']
        logs = delete_photos(filePaths)
        # print(logs)
        Response = BasicResponse(logs['status'],
                                 logs['operation'],
                                 logs['failedPath'],
                                 logs['totalNum'],
                                 logs['successNum'],
                                 logs['failedNum'],
                                 logs['description'])
        serializer = BasicResponseSerializer(Response)
        return JsonResponse(serializer.data)

# 移动图片
class MovingView(View):
    def post(self,request):
        requestTemp = json.loads(request.body)
        filePaths = requestTemp['filePath']
        folderPath = requestTemp['folderPath']
        logs = move_photos(filePaths,folderPath)
        Response = BasicResponse(logs['status'],
                                 logs['operation'],
                                 logs['failedPath'],
                                 logs['totalNum'],
                                 logs['successNum'],
                                 logs['failedNum'],
                                 logs['description'])
        serializer = BasicResponseSerializer(Response)
        return JsonResponse(serializer.data)