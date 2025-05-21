# -*- coding: utf-8 -*-
from datetime import datetime

from pyexiv2 import Image as ImgPyexiv
import rawpy
import os
import shutil
import time
from send2trash import send2trash
from functools import wraps
from PIL import Image
import piexif
# noinspection PyUnresolvedReferences
from apps.photos.utils_set.get_time import get_image_time
# noinspection PyUnresolvedReferences
from photos.models import photoIndex
from django.db.models.functions import ExtractMonth,ExtractDay

# noinspection PyUnresolvedReferences

# 修饰器 - 为返回结果添加时间戳
def add_timestamp(func):
    @wraps(func)
    def this_add(*args, **kwargs):
        response = func(*args, **kwargs)
        response['timestamp'] = time.time()
        return response

    return this_add


# 规定基本返回格式
def response_Type(filePaths: list, operation: str) -> dict:
    return {
        'status': 1,
        'operation': operation,
        'failedPath': [],
        'totalNum': len(filePaths),
        'successNum': 0,
        'failedNum': 0,
        'description': '',
        'timestamp': 0,
    }


# 对最后的返回字典相同部分进行统一处理，减少代码量，函数中的字典为引用对象，固可以对原字典进行直接修改
def response_unified_changed(response: dict, description_words: str):
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
def conflict_rename(filePath: str) -> str:
    count = 0
    dirname = os.path.dirname(filePath)
    filename, extension = os.path.splitext(os.path.basename(filePath))
    while True:
        tempPath = os.path.join(dirname, filename + (f'_{count}' if count != 0 else '') + extension)
        if os.path.exists(tempPath):
            count += 1
        else:
            return tempPath


# 删除文件
@add_timestamp
def delete_photos(filePaths: list[str]):
    response = response_Type(filePaths, 'delete')
    if response['totalNum'] == 0:
        response['status'] = 0
        response['description'] = '未选择任何文件'
        return response
    for filePath in filePaths:
        if not os.path.isfile(filePath):
            response['failedPath'].append({
                'path': filePath,
                'description': '文件不存在'
            })
            continue
        try:
            send2trash(filePath)
        except OSError as e:
            response['failedPath'].append({
                'path': filePath,
                'description': str(e)
            })
    response_unified_changed(response, '删除')
    return response


# 剪切（移动）/复制 文件到指定目录

@add_timestamp
def copy_move_photos(filePaths: list[str], folderPath: str, operation: str):
    response = response_Type(filePaths, operation)
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
                'path': filePath,
                'description': '文件不存在'
            })
            continue
        # 若操作为移动，则判断文件本身是否已经存在于所指定的目录
        if os.path.dirname(filePath) == folderPath and operation == 'move':
            response['failedPath'].append({
                'path': filePath,
                'description': '该文件所在文件夹为指定文件夹，无法移动'
            })
            continue
        # 获取指定目录下的新文件路径
        newfilePath = conflict_rename(os.path.join(folderPath, os.path.basename(filePath)))
        # 开始移动/复制
        try:
            shutil.move(filePath, newfilePath) if operation == 'move' else shutil.copy(filePath, newfilePath)
        except FileExistsError as e:
            response['failedPath'].append({
                'path': filePath,
                'description': e
            })
            continue
    response_unified_changed(response, '移动' if operation == 'move' else '复制')
    return response


# 格式转换，支持JPGE,PNG,GIF,WebP,BMP,TIFF,ICO,以及相机原始格式RAW转换为JPEG
# 格式后缀字典
format_suffix = {
    'JPEG': '.jpg',
    'PNG': '.png',
    'GIF': '.gif',
    'WebP': '.webp',
    'BMP': '.bmp',
    'TIFF': '.tiff',
    'ICO': '.ico',
}


def return_format_suffix():
    return list(format_suffix.keys())


print(return_format_suffix())
Camera_format_suffix = ['.nef', '.nrw']


@add_timestamp
def format_convert(filePaths, folderPath):
    response = response_Type(filePaths, 'format')
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
                'path': filePath,
                'description': '文件不存在'
            })
            continue
        # 检查转换后的文件在指定目录是否存在，存在则使用新名称
        filename, extension_temp = os.path.splitext(os.path.basename(filePath[0]))
        extension = format_suffix[filePath[1]]  # 获取新后缀
        newfilePath = conflict_rename(os.path.join(folderPath, str(filename + extension)))
        # 开始转换
        # 判断是否为相机原始格式，若为相机原始格式则使用rawpy库进行转换
        if extension_temp.lower() not in Camera_format_suffix:
            try:
                with Image.open(filePath[0]) as img:
                    # 若为PNG格式且为RGBA或LA模式，则转换为RGB模式
                    if extension_temp.lower() == '.png' and filePath[1].upper() == 'JPEG':
                        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                            img = img.convert('RGB')
                    img.save(newfilePath, format=filePath[1].upper())
            except Exception as e:
                response['failedPath'].append({
                    'path': filePath,
                    'description': str(e)
                })
                continue
        else:
            try:
                # 使用 pyexiv2 读取原始 RAW 文件的元数据
                with ImgPyexiv(filePath[0], encoding='GBK') as src_img:
                    metadata = src_img.read_exif()
                    # 获取原始方向标签
                    original_orientation = metadata.get('Exif.Image.Orientation', 1)
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
                if filePath[1] == 'JPEG':
                    with ImgPyexiv(newfilePath, encoding='GBK') as dst_img:
                        # 移除或重置方向标签（像素数据已校正，避免查看器再次旋转）
                        if 'Exif.Image.Orientation' in metadata:
                            metadata['Exif.Image.Orientation'] = 1  # 设为 1 表示正常方向
                        # 正确设置尺寸（不交换宽高）
                        metadata['Exif.Photo.PixelXDimension'] = img.width
                        metadata['Exif.Photo.PixelYDimension'] = img.height
                        dst_img.modify_exif(metadata)
            except Exception as e:
                response['failedPath'].append({
                    'path': filePath,
                    'description': str(e)
                })
                continue
    response_unified_changed(response, '格式转换')
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
def rename_photos(filePaths: list[list[str]], option: str, renameFormat: str):
    response = response_Type(filePaths, f'rename<{option}>')
    if response['totalNum'] == 0:
        response['status'] = 0
        response['description'] = '未选择任何文件'
        return response
    for filePath in filePaths:
        # 判断文件是否存在
        if not os.path.isfile(filePath[0]):
            response['failedPath'].append({
                'path': filePath,
                'description': '文件不存在'
            })
            continue
        # 自定义重命名
        filename, extension_temp = os.path.splitext(os.path.basename(filePath[0]))
        if option == 'custom':
            if filename == filePath[1]:
                response['failedPath'].append({
                    'path': filePath,
                    'description': '新名称与原名称相同'
                })
                continue
            newfilePath = conflict_rename(os.path.join(os.path.dirname(filePath[0]), str(filePath[1] + extension_temp)))
            try:
                os.rename(filePath[0], newfilePath)
            except Exception as e:
                response['failedPath'].append({
                    'path': filePath,
                    'description': str(e)
                })
                continue
        else:
            # 按照指定格式重命名
            try:
                newfileName = get_image_time(filePath[0], renameFormat)
                if newfileName == filename:
                    response['failedPath'].append({
                        'path': filePath,
                        'description': '新名称与原名称相同'
                    })
                    continue
                newfilePath = conflict_rename(
                    os.path.join(os.path.dirname(filePath[0]), str(newfileName + extension_temp)))
                os.rename(filePath[0], newfilePath)
            except Exception as e:
                response['failedPath'].append({
                    'path': filePath,
                    'description': str(e)
                })
                continue
    response_unified_changed(response, '重命名')
    return response


@add_timestamp
def crop_image(filePaths: list[list[str]], folderPath):
    response = response_Type(filePaths, 'crop')

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
                'path': filePath,
                'description': '文件不存在'
            })
            continue

        try:
            filename, extension_temp = os.path.splitext(os.path.basename(filePath[0]))
            # 读取原始图片的 EXIF 数据
            exif_dict = {}
            with Image.open(filePath[0]) as img:
                exif_data = img._getexif()
                if exif_data:
                    exif_dict = piexif.load(exif_data)
                width, height = img.size
                # 计算图片的裁剪大小
                left, left_top, right, right_bottom = width * filePath[1][0], height * filePath[1][1], width * \
                                                      filePath[1][2], height * filePath[1][3]
                # 裁剪图片
                cropped_img = img.crop((left, left_top, right, right_bottom))
                # 保存裁剪后的图片
                newfilePath = conflict_rename(os.path.join(folderPath, str(filename + extension_temp)))
                # 写入元信息
                if exif_dict:
                    exif_bytes = piexif.dump(exif_dict)
                    cropped_img.save(newfilePath, exif=exif_bytes)
                else:
                    cropped_img.save(newfilePath)
        except Exception as e:
            response['failedPath'].append({
                'path': filePath,
                'description': str(e)
            })
        return response


# 获取元信息
@add_timestamp
def getEditExif(filePath: str):
    if not os.path.isfile(filePath):
        return {
            'status': 0,
            'description': '文件不存在',
            'camera_info': {},
            'photo_info': {},
        }
    else:
        try:
            with ImgPyexiv(filePath, encoding='GBK') as img:
                exif_data = img.read_exif()
                camera_info = {
                    "equipment_brand": exif_data.get("Exif.Image.Make", "未知"),
                    "equipment_model": exif_data.get("Exif.Image.Model", "未知"),
                    "shooting_time": exif_data.get("Exif.Photo.DateTimeOriginal", "未知"),
                    "lens_model": exif_data.get('Exif.Photo.LensModel', "未知")
                }
                # 提取拍摄参数
                photo_info = {
                    "aperture": exif_data.get("Exif.Photo.FNumber", "未知"),
                    "shutter_speed": exif_data.get("Exif.Photo.ExposureTime", "未知"),
                    "ISO": exif_data.get("Exif.Photo.ISOSpeedRatings", "未知"),
                    "focal_length": exif_data.get("Exif.Photo.FocalLength", "未知"),
                }
        except Exception as e:
            return {
                'status': 0,
                'description': str(e),
                'camera_info': {},
                'photo_info': {},
            }
        return {
            'status': 1,
            'description': '获取成功',
            'camera_info': camera_info,
            'photo_info': photo_info,
        }


# 设置元数据
@add_timestamp
def setEditExif(filePath: str, camera_info: dict, photo_info: dict):
    if not os.path.isfile(filePath):
        return {
            'status': 0,
            'description': '文件不存在',
        }
    else:
        try:
            with ImgPyexiv(filePath, encoding='GBK') as img:
                # 读取现有 EXIF 数据
                exif_data = img.read_exif()
                # 更新相机信息
                if camera_info:
                    # 映射自定义键到 EXIF 标签
                    exif_mapping = {
                        "equipment_brand": "Exif.Image.Make",
                        "equipment_model": "Exif.Image.Model",
                        "shooting_time": "Exif.Photo.DateTimeOriginal",
                        "lens_model": "Exif.Photo.LensModel"
                    }
                    for key, value in camera_info.items():
                        if key in exif_mapping and value is not None:
                            exif_tag = exif_mapping[key]
                            # 特殊处理：拍摄时间需要符合 "YYYY:MM:DD HH:MM:SS" 格式
                            if key == "shooting_time" and not value.endswith((':', ' ')):
                                # 尝试格式化时间
                                try:
                                    from datetime import datetime
                                    dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                                    value = dt.strftime("%Y:%m:%d %H:%M:%S")
                                except:
                                    pass
                            exif_data[exif_tag] = value

                # 更新拍摄参数
                if photo_info:
                    exif_mapping = {
                        "aperture": "Exif.Photo.FNumber",
                        "shutter_speed": "Exif.Photo.ExposureTime",
                        "ISO": "Exif.Photo.ISOSpeedRatings",
                        "focal_length": "Exif.Photo.FocalLength"
                    }

                    for key, value in photo_info.items():
                        if key in exif_mapping and value is not None:
                            exif_tag = exif_mapping[key]

                            # 特殊处理：光圈值（转换为有理数格式）
                            if key == "aperture" and isinstance(value, str) and value.startswith("f/"):
                                try:
                                    f_number = float(value.replace("f/", ""))
                                    exif_data[exif_tag] = f_number
                                except:
                                    pass

                            # 特殊处理：快门速度（转换为有理数格式）
                            elif key == "shutter_speed":
                                try:
                                    if isinstance(value, str) and "/" in value:
                                        num, denom = map(int, value.split("/"))
                                        exif_data[exif_tag] = (num, denom)  # 分数形式
                                    else:
                                        exif_data[exif_tag] = float(value)  # 小数形式
                                except:
                                    pass

                            # 特殊处理：焦距（转换为浮点数）
                            elif key == "focal_length":
                                try:
                                    exif_data[exif_tag] = float(value)
                                except:
                                    pass
                            # 其他参数直接设置
                            else:
                                exif_data[exif_tag] = value

                # 写入修改后的 EXIF 数据
                img.modify_exif(exif_data)
        except Exception as e:
            return {
                'status': 0,
                'description': str(e),
            }
        return {
            'status': 1,
            'description': '设置成功',
        }


# print(setEditExif("O:\\0-项目\\IMAGE_MANAGEMENT\\temp_photos\\2024-09.NEF",
#                   {
#                       "equipment_brand": "NIKON",
#                       "equipment_model": "NIKON Z 5",
#                       "shooting_time": "2024:11:02 15:53:49",
#                       "lens_model": "NIKKOR Z 24-200mm f/4-6.3 VR"
#                   },
#                   {
#                       "aperture": "56/10",
#                       "shutter_speed": "1/250",
#                       "ISO": "400",
#                       "focal_length": "520/10"
#                   }))
# print(getEditExif("O:\\0-项目\\IMAGE_MANAGEMENT\\temp_photos\\2024-09.NEF"))
# 增加水印或添加边框
# def watermark_image()

def getDict(date_type: str):
    return {
        'total': 0,
        'date_type': date_type
    }

@add_timestamp
def getAllInfo():
    response = {'status': 1, 'description': '','total_photo': photoIndex.objects.count(), 'date': getDict('years'), }
    years = [y['date__year'] for y in photoIndex.objects.values('date__year').distinct()]
    response['date']['total'] = len(years)
    for y in years:
        response['date'][str(y)] = getDict('months')
        months = photoIndex.objects.filter(
            date__year=y
        ).annotate(
            month = ExtractMonth('date')
        ).values_list(
            'month',flat=True
        ).distinct().order_by('month')
        response['date'][str(y)]['total'] = len(months)
        for m in months:
            response['date'][str(y)][str(m)] = getDict('days')
            days = photoIndex.objects.filter(
                date__year=y,
                date__month=m
            ).annotate(
                day = ExtractDay('date')
            ).values_list(
                'day',flat=True
            ).distinct().order_by('day')
            response['date'][str(y)][str(m)]['total'] = len(days)
            for d in days:
                response['date'][str(y)][str(m)][str(d)] = getDict('photos')
                photos_num = photoIndex.objects.filter(
                    date = datetime.strptime(f'{y}-{m}-{d}', "%Y-%m-%d").date()
                ).count()
                response['date'][str(y)][str(m)][str(d)]['total'] = photos_num
    return response
