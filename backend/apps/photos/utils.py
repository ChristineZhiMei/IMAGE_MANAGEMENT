# -*- coding: utf-8 -*-
import os
import time

from send2trash import send2trash

def delete_photos(filePaths):
    response = {
        'status':1,
        'operation':'delete',
        'failedPath':[],
        'totalNum':len(filePaths),
        'successNum':0,
        'failedNum':0,
        'description':'删除成功',
        'timestamp':time.time(),
    }
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
    response['failedNum'] = len(response['failedPath'])
    response['successNum'] = response['totalNum'] - response['failedNum']
    if response['totalNum'] > 0:
        if response['failedNum'] == 0:
            response['status'] = 1
            response['description'] = '全部删除成功'
        elif response['successNum'] == 0:
            response['status'] = 0
            response['description'] = '全部删除失败'
        else:
            response['status'] = -1
            response['description'] = '部分删除成功'
    return response