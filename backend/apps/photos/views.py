import asyncio
import json
import time

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.urls import resolve
# noinspection PyUnresolvedReferences
from apps.photos.serializers import DefaultInfo,DefaultSerializer,BasicResponse,BasicResponseSerializer,EditExifResponse,EditExifResponseSerializer,DateStructureSerializer
# noinspection PyUnresolvedReferences
from apps.photos.utils import delete_photos,copy_move_photos,format_convert,rename_photos,crop_image,getEditExif,setEditExif,getAllInfo,getPhotoList
# noinspection PyUnresolvedReferences
from config import ConfigController
# noinspection PyUnresolvedReferences
from apps.photos.utils_set.build_index import process_files_in_directory,create_Index

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
class CopyMovingView(View):
    def post(self,request):
        # 反向解析url路径名称
        match = resolve(request.path_info)
        url_pattern = match.route.replace('/','')
        #
        requestTemp = json.loads(request.body)
        filePaths = requestTemp['filePath']
        folderPath = requestTemp['folderPath']
        logs = copy_move_photos(filePaths,folderPath,url_pattern)
        Response = BasicResponse(logs['status'],
                                 logs['operation'],
                                 logs['failedPath'],
                                 logs['totalNum'],
                                 logs['successNum'],
                                 logs['failedNum'],
                                 logs['description'])
        serializer = BasicResponseSerializer(Response)
        return JsonResponse(serializer.data)

# 图片格式转换
class FormatConvertView(View):
    def post(self,request):
        requestTemp = json.loads(request.body)
        filePaths = requestTemp['filePath']
        folderPath = requestTemp['folderPath']
        logs = format_convert(filePaths,folderPath)
        Response = BasicResponse(logs['status'],
                                 logs['operation'],
                                 logs['failedPath'],
                                 logs['totalNum'],
                                 logs['successNum'],
                                 logs['failedNum'],
                                 logs['description'])
        serializer = BasicResponseSerializer(Response)
        return JsonResponse(serializer.data)

# 图片重命名
class RenameView(View):
    def post(self,request):
        requestTemp = json.loads(request.body)
        filePaths = requestTemp['filePath']
        option = requestTemp['option']
        renameFormat = requestTemp['renameFormat']
        logs = rename_photos(filePaths,option,renameFormat)
        Response = BasicResponse(logs['status'],
                                 logs['operation'],
                                 logs['failedPath'],
                                 logs['totalNum'],
                                 logs['successNum'],
                                 logs['failedNum'],
                                 logs['description'])
        serializer = BasicResponseSerializer(Response)
        return JsonResponse(serializer.data)

class CropView(View):
    def post(self,request):
        requestTemp = json.loads(request.body)
        filePaths = requestTemp['filePath']
        folderPath = requestTemp['folderPath']
        logs = crop_image(filePaths,folderPath)
        Response = BasicResponse(logs['status'],
                                 logs['operation'],
                                 logs['failedPath'],
                                 logs['totalNum'],
                                 logs['successNum'],
                                 logs['failedNum'],
                                 logs['description'])
        serializer = BasicResponseSerializer(Response)
        return JsonResponse(serializer.data)

class EditExifView(View):
    def post(self,request):
        match = resolve(request.path_info)
        url_pattern = match.route
        print(url_pattern)
        if url_pattern == 'edit/getExif/':
            filePath = json.loads(request.body)['filePath']
            logs = getEditExif(filePath)
            Response = EditExifResponse(logs['status'],
                                        logs['description'],
                                        logs['camera_info'],
                                        logs['photo_info'])
            serializer = EditExifResponseSerializer(Response)
            return JsonResponse(serializer.data)
        elif url_pattern == 'edit/setExif/':
            filePath = json.loads(request.body)['filePath']
            camera_info = json.loads(request.body)['camera_info']
            photo_info = json.loads(request.body)['photo_info']
            logs = setEditExif(filePath,camera_info,photo_info)
            return JsonResponse(logs)

class LoadView(View):
    async def get(self,request):
        print(configSG.get_setting()[0])
        if configSG.get_setting()[0] == '':
            return JsonResponse({
                'status':0,
                'description':'选择目录不可用'
            })
        await process_files_in_directory(configSG.get_setting()[0],10)
        # await create_Index(r'O:\0-项目\IMAGE_MANAGEMENT\temp_photos\DSC_8486-已增强-降噪.dng')
        return JsonResponse({
            'status':1,
            'description':'构建成功'
        })

class GetAllInfoView(View):
     def get(self,request):
        logs = getAllInfo()
        # serializer = DateStructureSerializer(logs)
        return JsonResponse(logs)

class GettingPhotoListView(View):
    def get(self,request,year,month,day):
        return JsonResponse(getPhotoList(year,month,day))
