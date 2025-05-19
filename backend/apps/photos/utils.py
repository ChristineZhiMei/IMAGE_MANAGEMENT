# -*- coding: utf-8 -*-
import rawpy
import os
import shutil
import time
from send2trash import send2trash
from functools import wraps
from PIL import Image

# noinspection PyUnresolvedReferences
from apps.photos.utils_set.get_time import get_image_time


# 修饰器 - 为返回结果添加时间戳
def add_timestamp(func):
    @wraps(func)
    def this_add(*args,**kwargs):
        response = func(*args,**kwargs)
        response['timestamp'] = time.time()
        return response
    return this_add

# 规定基本返回格式
def response_Type(filePaths:list,operation:str) -> dict:
    return {
        'status':1,
        'operation':operation,
        'failedPath':[],
        'totalNum':len(filePaths),
        'successNum':0,
        'failedNum':0,
        'description':'',
        'timestamp':0,
    }
# 对最后的返回字典相同部分进行统一处理，减少代码量，函数中的字典为引用对象，固可以对原字典进行直接修改
def response_unified_changed(response:dict,description_words:str):
    response['failedNum'] = len(response['failedPath'])
    response['successNum'] = response['totalNum'] - response['failedNum']
    if response['totalNum'] > 0:
        if response['failedNum'] == 0:
            response['status'] = 1
            response['description'] = f'全部{description_words}成功'
        elif response['successNum'] == 0:
            response['status'] = 0
            response['description'] = f'全部{description_words}失败'
        else:
            response['status'] = -1
            response['description'] = f'部分{description_words}成功'
# 检测文件重名并返回新名称
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

# 删除文件
@add_timestamp
def delete_photos(filePaths:list[str]):
    response = response_Type(filePaths,'delete')
    if response['totalNum'] == 0:
        response['status'] = 0
        response['description'] = '未选择任何文件'
        return response
    for filePath in filePaths:
        if not os.path.isfile(filePath):
            response['failedPath'].append({
                'path':filePath,
                'description':'文件不存在'
            })
            continue
        try:
            send2trash(filePath)
        except OSError as e:
            response['failedPath'].append({
                'path':filePath,
                'description':str(e)
            })
    response_unified_changed(response,'删除')
    return response


# 剪切（移动）/复制 文件到指定目录

@add_timestamp
def copy_move_photos(filePaths:list[str],folderPath:str,operation:str):
    response = response_Type(filePaths,operation)
    if response['totalNum'] == 0:
        response['status'] = 0
        response['description'] = '未选择任何文件'
        return response
    # 判断指定路径是否为目录
    if not os.path.isdir(folderPath):
        response['status'] = 0
        response['description'] = '指定目录不存在'
        return response
    for filePath in filePaths:
        # 判断文件是否存在
        if not os.path.isfile(filePath):
            response['failedPath'].append({
                'path':filePath,
                'description':'文件不存在'
            })
            continue
        # 若操作为移动，则判断文件本身是否已经存在于所指定的目录
        if os.path.dirname(filePath) == folderPath and operation == 'move':
            response['failedPath'].append({
                'path':filePath,
                'description':'该文件所在文件夹为指定文件夹，无法移动'
            })
            continue
        # 获取指定目录下的新文件路径
        newfilePath = conflict_rename(os.path.join(folderPath,os.path.basename(filePath)))
        # 开始移动/复制
        try:
            shutil.move(filePath, newfilePath) if operation == 'move' else shutil.copy(filePath, newfilePath)
        except FileExistsError as e:
            response['failedPath'].append({
                'path':filePath,
                'description':e
            })
            continue
    response_unified_changed(response,'移动' if operation == 'move' else '复制')
    return response

# 格式转换，支持JPGE,PNG,GIF,WebP,BMP,TIFF,ICO,以及相机原始格式RAW转换为JPEG
# 格式后缀字典
format_suffix = {
    'JPEG':'.jpg',
    'PNG':'.png',
    'GIF':'.gif',
    'WebP':'.webp',
    'BMP':'.bmp',
    'TIFF':'.tiff',
    'ICO':'.ico',
}
Camera_format_suffix = ['.nef', '.nrw']
@add_timestamp
def format_convert(filePaths,folderPath):
    response = response_Type(filePaths,'format')
    if response['totalNum'] == 0:
        response['status'] = 0
        response['description'] = '未选择任何文件'
        return response
    # 判断指定路径是否为目录
    if not os.path.isdir(folderPath):
        response['status'] = 0
        response['description'] = '指定目录不存在'
        return response
    for filePath in filePaths:
        # 判断文件是否存在
        if not os.path.isfile(filePath[0]):
            response['failedPath'].append({
                'path':filePath,
                'description':'文件不存在'
            })
            continue
        # 检查转换后的文件在指定目录是否存在，存在则使用新名称
        filename, extension_temp = os.path.splitext(os.path.basename(filePath[0]))
        extension = format_suffix[filePath[1]] # 获取新后缀
        newfilePath =  conflict_rename(os.path.join(folderPath,str(filename + extension)))
        # 开始转换
        # 判断是否为相机原始格式，若为相机原始格式则使用rawpy库进行转换
        if extension_temp.lower() not in Camera_format_suffix:
            try:
                with Image.open(filePath[0]) as img:
                    # 若为PNG格式且为RGBA或LA模式，则转换为RGB模式
                    if extension_temp.lower() == '.png' and filePath[1].upper() == 'JPEG':
                        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                            img = img.convert('RGB')
                    img.save(newfilePath,format=filePath[1].upper())
            except Exception as e:
                response['failedPath'].append({
                    'path':filePath,
                    'description':str(e)
                })
                continue
        else:
            try:
                # 读取RAW文件
                with rawpy.imread(filePath[0]) as raw:
                    # 使用相机预设的白平衡
                    rgb = raw.postprocess(
                        use_camera_wb=True,
                        output_color=rawpy.ColorSpace.sRGB,
                        no_auto_bright=True,
                        bright=1.0,  # 可尝试调整到 2.0 或更高
                        gamma=(2.2, 4.5),
                    )
                    img = Image.fromarray(rgb)
                    img.save(newfilePath, quality=95, subsampling=0)
            except Exception as e:
                response['failedPath'].append({
                    'path':filePath,
                    'description':str(e)
                })
                continue
    response_unified_changed(response,'格式转换')
    return response
# 图片重命名
# 命名格式 YYYY-MMDD-HHMMSS_X X为序号，若重复则从1开始
# 举例2025年1月1日1时1分1秒
# name_format = ['YYYY-MMDD-HHMMSS',# 完整年-月-日-时-分-秒 2025-0101-010101
#                'YYYY-MMDD-HHMM',# 完整年-月-日-时-分 2025-0101-0101
#                'YYYY-MMDD-HH',# 完整年-月-日-时 2025-0101-01
#                'YYYY-MMDD',# 完整年-月-日 2025-0101
#                'YYYY-MM',# 完整年-月 2025-01
#                'YY-MMDD-HHMMSS',# 后两位年-月-日-时-分-秒 25-0101-010101
#                'YY-MMDD-HHMM',# 后两位年-月-日-时-分 25-0101-0101
#                'YY-MMDD-HH'# 后两位年-月-日-时 25-0101-01
#                'YY-MMDD',# 后两位年-月-日 25-0101
#                'YY-MM'# 后两位年-月 25-01
#                ]
@add_timestamp
def rename_photos(filePaths:list[list[str]],option:str,renameFormat:str):
    response = response_Type(filePaths,f'rename<{option}>')
    if response['totalNum'] == 0:
        response['status'] = 0
        response['description'] = '未选择任何文件'
        return response
    for filePath in filePaths:
        # 判断文件是否存在
        if not os.path.isfile(filePath[0]):
            response['failedPath'].append({
                'path':filePath,
                'description':'文件不存在'
            })
            continue
        # 自定义重命名
        filename,extension_temp = os.path.splitext(os.path.basename(filePath[0]))
        if option == 'custom':
            if filename == filePath[1]:
                response['failedPath'].append({
                    'path':filePath,
                    'description':'新名称与原名称相同'
                })
                continue
            newfilePath = conflict_rename(os.path.join(os.path.dirname(filePath[0]),str(filePath[1] + extension_temp)))
            try:
                os.rename(filePath[0],newfilePath)
            except Exception as e:
                response['failedPath'].append({
                    'path':filePath,
                    'description':str(e)
                })
                continue
        else:
            # 按照指定格式重命名
            try:
                newfileName = get_image_time(filePath[0],renameFormat)
                if newfileName == filename:
                    response['failedPath'].append({
                        'path':filePath,
                        'description':'新名称与原名称相同'
                    })
                    continue
                newfilePath = conflict_rename(os.path.join(os.path.dirname(filePath[0]),str(newfileName + extension_temp)))
                os.rename(filePath[0],newfilePath)
            except Exception as e:
                response['failedPath'].append({
                    'path':filePath,
                    'description':str(e)
                })
                continue
    response_unified_changed(response,'重命名')
    return response