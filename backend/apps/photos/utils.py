# -*- coding: utf-8 -*-
import os
import shutil
import time
from send2trash import send2trash
from functools import wraps

# 修饰器 - 为返回结果添加时间戳
def add_timestamp(func):
    @wraps(func)
    def this_add(*args,**kwargs):
        response = func(*args,**kwargs)
        response['timestamp'] = time.time()
        return response
    return this_add

# 规定基本返回格式
def response_Type(filePaths:list[str],operation:str) -> dict:
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
def conflict_rename(filepath:str) -> str:
    count = 0
    dirname = os.path.dirname(filepath)
    filename, extension = os.path.splitext(os.path.basename(filepath))
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