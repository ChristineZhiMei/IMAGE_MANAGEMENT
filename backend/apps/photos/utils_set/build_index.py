# -*- coding: utf-8 -*-
import uuid
import os
import pandas as pd
import rawpy
from pathlib import Path
from PIL import Image
from django.conf import settings

from photos.models import photoIndex


from apps.photos.utils_set.get_time import get_image_time
from config import ConfigController

# 获取文件日期->创建日期目录->创建&读取索引文件CSV->生成缩略图并获取返回路径->
# 将原图路径和缩略图路径写入索引文件CSV->返回索引日期,文件路径,最新文件数量->写入表层目录索引文件CSV(日期，路径,该日期下文件数量)

# 检测文件重名并返回新名称
configSG = ConfigController()

def conflict_rename(filePath:str) -> str:
    count = 0
    dirname = os.path.dirname(filePath)
    filename, extension = os.path.splitext(os.path.basename(filePath))
    while True:
        tempPath = os.path.join(dirname,filename+(f'_{count}' if count != 0 else '')+extension)
        if os.path.exists(tempPath):
            count += 1
        else:
            return tempPath

# 生成缩略图到指定文件夹size = (256,256),并返回新文件路径
def generate_thumbnail(filePath:str,folderPath:str,size,delete:bool=False):
    if not os.path.isfile(filePath) or not os.path.isdir(folderPath):
        return None
    filename, extension = os.path.splitext(os.path.basename(filePath))
    newfilePath = conflict_rename(os.path.join(folderPath,('cache_' + filename + '.webp')))
    # 如果格式不存在则转换为JPEG格式再转换为WEBP格式
    if extension.lower() not in ['.jpg','.jpeg','.png','.webp']:
        with rawpy.imread(filePath) as raw:
            # 使用相机预设的白平衡
            rgb = raw.postprocess(
                use_camera_wb=True,
                output_color=rawpy.ColorSpace.sRGB,
                no_auto_bright=True,
                bright=1.0,  # 可尝试调整到 2.0 或更高
                gamma=(2.2, 4.5),
            )
            img = Image.fromarray(rgb)
            tempFilePath = conflict_rename(os.path.join(folderPath, filename + '.jpg'))
            img.save(tempFilePath, quality=95, subsampling=0)
            generate_thumbnail(tempFilePath,folderPath,size,True)
    else:
        with Image.open(filePath) as img:
            img.thumbnail(size,resample=Image.Resampling.LANCZOS)
            # 获取指定目录下的新文件路径
            img.save(newfilePath,format='WEBP')
        if delete:
            os.remove(filePath)
        return newfilePath

# 根据日期在缓存目录创建目录
def create_date_dir(date:str):
    cachePath = configSG.get_setting()[1]
    newDate = date.split('-')
    newDate[0] = 'Y'+newDate[0]
    newDate.append('D'+newDate[1][2:])
    newDate[1] = 'M'+newDate[1][0:2]
    endPath = os.path.join(cachePath,'/'.join(newDate))
    if not os.path.exists(endPath):
        os.makedirs(endPath)
    return endPath

def creat_Index(path:str):
    if not os.path.exists(path):
        print('123')
        return False
    try:
        time = get_image_time(path,'YYYY-MMDD')
        endPath = create_date_dir(time)
        print(time,endPath)
        # 生成缩略图
        time = time[0:-2]+'-'+time[-2:]
        thumbnailPath = generate_thumbnail(path,endPath,(600,600))
        photoIndex.objects.create(date = time,filePath = path,thumbnailPath = thumbnailPath)
    except Exception as e:
        print(f"创建索引失败: {e}")
        return False
    return True