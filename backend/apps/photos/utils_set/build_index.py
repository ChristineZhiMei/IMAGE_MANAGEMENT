# -*- coding: utf-8 -*-
import asyncio
import os
import shutil

import rawpy
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from functools import partial


# 服务器
from photos.models import photoIndex
from apps.photos.utils_set.get_time import get_image_time
from config import ConfigController
# 测试时
from asgiref.sync import sync_to_async
from win32comext.shell.demos.servers.folder_view import folderViewImplContextMenuIDs


# from backend.apps.photos.models import photoIndex
# from backend.apps.photos.utils_set.get_time import get_image_time
# from backend.config.config import ConfigController



# 获取文件日期->创建日期目录->创建&读取索引文件CSV->生成缩略图并获取返回路径->
# 将原图路径和缩略图路径写入索引文件CSV->返回索引日期,文件路径,最新文件数量->写入表层目录索引文件CSV(日期，路径,该日期下文件数量)
allNum = 0
SuccessNum = 0
# 检测文件重名并返回新名称
configSG = ConfigController()
create_photo_index = sync_to_async(photoIndex.objects.update_or_create)
delete_photos_index = sync_to_async(photoIndex.objects.all().delete)
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
    # print('开始生成缩略图')
    if not os.path.isfile(filePath) or not os.path.isdir(folderPath):
        return None
    filename, extension = os.path.splitext(os.path.basename(filePath))
    newfilePath = conflict_rename(os.path.join(folderPath,('cache_' + filename + '.webp')))
    # 如果格式不存在则转换为JPEG格式再转换为WEBP格式
    if extension.lower() not in ['.jpg','.jpeg','.png','.webp']:
        raise ValueError('不支持的文件格式'+extension)
        # with rawpy.imread(filePath) as raw:
        #     # 使用相机预设的白平衡
        #     rgb = raw.postprocess(
        #         use_camera_wb=True,
        #         output_color=rawpy.ColorSpace.sRGB,
        #         no_auto_bright=False,
        #         bright=1.0,  # 可尝试调整到 2.0 或更高
        #         gamma=(2.2, 4.5),
        #     )
        #     img = Image.fromarray(rgb)
        #     tempFilePath = conflict_rename(os.path.join(folderPath, filename + '.jpg'))
        #     img.save(tempFilePath, quality=95, subsampling=0)
        #     generate_thumbnail(tempFilePath,folderPath,size,True)
    else:
        with Image.open(filePath) as img:
            img.thumbnail(size,resample=Image.Resampling.LANCZOS)
            # 获取指定目录下的新文件路径
            img.save(newfilePath,format='WEBP')
        if delete:
            os.remove(filePath)
    # print('已生成缩略图')
    return newfilePath

# 根据日期在缓存目录创建目录
def create_date_dir(date:str):
    cachePath = configSG.get_setting()[1]
    newDate = date.split('-')
    newDate[0] = 'Y'+newDate[0]
    newDate.append('D'+newDate[1][2:])
    newDate[1] = 'M'+newDate[1][0:2]
    endPath = os.path.join(cachePath,*newDate)
    try:
        if not os.path.exists(os.path.abspath(endPath)):
            os.makedirs(endPath)
    except Exception as e:
        pass
    return str(endPath)


async def create_Index(path:str):
    if not os.path.exists(path):
        return False
    try:
        time = get_image_time(path,'YYYY-MMDD')
        endPath = create_date_dir(time)
        # 生成缩略图
        time2 = time[0:-2]+'-'+time[-2:]
        thumbnailPath = await asyncio.to_thread(generate_thumbnail,path,endPath,(600,600))
        print('生成成功')
        await create_photo_index(filePath=path, defaults = {'date':time2, 'thumbnailPath':thumbnailPath,'classification':''})
    except Exception as e:
        print(e)
    return True

async def process_files_in_directory(directory:str,max_workers: int = 10) -> None:
    global allNum
    global SuccessNum
    allNum = 0
    SuccessNum = 0
    folderCachePath = configSG.get_setting()[1]
    try:
        print('清理缓存目录')
        for item in os.listdir(folderCachePath):
            item_path = os.path.join(folderCachePath, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        print('清理缓存完成')
        print('清理索引表')
        try:
            await delete_photos_index()
        except Exception as e:
            print(e)
        print('清理索引表完成')

    except Exception as e:
        print(e)
        return
    # 创建信号量限制并发数量
    semaphore = asyncio.Semaphore(max_workers)

    async def process_file(file_path: str) -> None:
        # 使用信号量控制并发
        async with semaphore:
            # 在线程池中执行异步函数
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                partial(asyncio.run, create_Index(file_path))
            )

    # 创建任务列表（不一次性生成所有任务）
    tasks = []

    # 遍历目录树
    for root, dirs, files in os.walk(directory, topdown=True):
        for name in files:
            _, extension = os.path.splitext(name)
            if extension.lower() not in ['.jpg','.jpeg','.png','.webp']:
                continue
            file_path = os.path.join(root, name)
            tasks.append(process_file(file_path))

            # 定期批量执行任务，避免内存过载
            if len(tasks) >= max_workers * 2:
                await asyncio.gather(*tasks)
                tasks.clear()
    # 执行剩余任务
    if tasks:
        await asyncio.gather(*tasks)