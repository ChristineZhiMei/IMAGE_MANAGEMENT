# -*- coding: utf-8 -*-
import os
import re
import sys
from datetime import datetime
from functools import wraps

import pyexiv2

format_dict = {
    'YYYY-MMDD-HHMMSS': {
        'regex': r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})',
        'replace': r'\1-\2\3-\4\5\6'
    },
    'YYYY-MMDD-HHMM': {
        'regex': r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):\d{2}',
        'replace': r'\1-\2\3-\4\5'
    },
    'YYYY-MMDD-HH': {
        'regex': r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):\d{2}:\d{2}',
        'replace': r'\1-\2\3-\4'
    },
    'YYYY-MMDD': {
        'regex': r'(\d{4})-(\d{2})-(\d{2}) \d{2}:\d{2}:\d{2}',
        'replace': r'\1-\2\3'
    },
    'YYYY-MM': {
        'regex': r'(\d{4})-(\d{2})-(\d{2}) \d{2}:\d{2}:\d{2}',
        'replace': r'\1-\2'
    },
    'YY-MMDD-HHMMSS': {
        'regex': r'\d{2}(\d{2})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})',
        'replace': r'\1-\2\3-\4\5\6'
    },
    'YY-MMDD-HHMM': {
        'regex': r'\d{2}(\d{2})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):\d{2}',
        'replace': r'\1-\2\3-\4\5'
    },
    'YY-MMDD-HH': {
        'regex': r'\d{2}(\d{2})-(\d{2})-(\d{2}) (\d{2}):\d{2}:\d{2}',
        'replace': r'\1-\2\3-\4'
    },
    'YY-MMDD': {
        'regex': r'\d{2}(\d{2})-(\d{2})-(\d{2}) \d{2}:\d{2}:\d{2}',
        'replace': r'\1-\2\3'
    },
    'YY-MM': {
        'regex': r'\d{2}(\d{2})-(\d{2})-(\d{2}) \d{2}:\d{2}:\d{2}',
        'replace': r'\1-\2'
    }
}
def time_format(func):
    @wraps(func)
    def convert_to_format(*args,**kwargs) -> str:
        standard_time, target_format = func(*args,**kwargs)
        if target_format not in format_dict:
            raise ValueError(f"不支持的格式: {target_format}")
        # 获取对应的正则表达式和替换模式
        pattern = format_dict[target_format]['regex']
        replace = format_dict[target_format]['replace']
        # 执行替换
        return re.sub(pattern, replace, standard_time)
    return convert_to_format
# 获取文件的创建时间
def get_create_time(file_path):
    try:
        # 获取文件的创建时间
        ctime = os.path.getctime(file_path)
        return datetime.fromtimestamp(ctime)
    except OSError as e:
        mtime = os.path.getmtime(file_path)
        return datetime.fromtimestamp(mtime)
# 通过元数据获取图片的拍摄时间
def get_exif_time(image_path):
    """使用 pyexiv2 获取图片的拍摄时间（支持 JPEG、TIFF、RAW 等格式）"""
    # try:
    #     if not os.path.exists(image_path):
    #         raise FileNotFoundError(f"文件不存在：{image_path}")
    #     with pyexiv2.Image(image_path, encoding='GBK') as image:
    #         var = image.read_exif()
    #     try:
    #         var = var['Exif.Image.DateTimeOriginal']
    #     except:
    #         try:
    #             var = var['Exif.Photo.DateTimeOriginal']  # 尝试获取DateTime作为备选
    #         except:
    #             return None
    try:
        with pyexiv2.Image(image_path,encoding='GBK') as image:
            metadata = image.read_exif()
            # 尝试常见的拍摄时间标签
            time_keys = [
                'Exif.Photo.DateTimeOriginal',  # 优先使用原始拍摄时间
                'Exif.Image.DateTimeOriginal',
                'Exif.Photo.DateTimeDigitized',
                'Exif.Image.DateTime'
            ]
            for key in time_keys:
                if key in metadata:
                    time_str = metadata[key]
                    # 处理可能的时区信息（格式如 "2023:05:20 12:30:45+08:00"）
                    if '+' in time_str or '-' in time_str:
                        time_str = time_str.split('+')[0].split('-')[0]
                    try:
                        return datetime.strptime(time_str, '%Y:%m:%d %H:%M:%S')
                    except ValueError as e:
                        print(f"时间格式解析失败: {e}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"读取元数据失败: {e}", file=sys.stderr)
        return None

@time_format
def get_image_time(image_path,target_format):
    # 优先尝试获取 EXIF 时间
    exif_time = get_exif_time(image_path)
    if exif_time:
        return str(exif_time),target_format
    # 若没有拍摄时间，获取创建时间
    create_time = str(get_create_time(image_path)).split('.')[0]
    return create_time,target_format

# 获取支持的日期格式
def get_format():
    return list(format_dict.keys())