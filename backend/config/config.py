# -*- coding: utf-8 -*-
import configparser
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_CACHE_DIR = os.path.join(BASE_DIR, 'cache')

class ConfigController:
    def __init__(self):
        # 获取当前脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(script_dir, "config.ini")

        self.config = configparser.ConfigParser()
        # 确保配置文件存在
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件 {self.config_path} 不存在")
        # 读取配置
        self.config.read(self.config_path, encoding='utf-8')
    # 获取设置中的路径
    def get_setting(self):
        # 读取路径
        read_path = self.config.get('Settings','read_path')
        cache_path = self.config.get('Settings','cache_path')
        # 判断路径是否可用
        if not os.path.isdir(read_path):
            # 不可用则重置为""
            self.config.set('Settings','read_path','')
            read_path = ''
        if not os.path.isdir(cache_path):
            # 不可用则重置为默认路径
            self.config.set('Settings','cache_path',BASE_CACHE_DIR)
            cache_path = BASE_CACHE_DIR
        with open(self.config_path, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
        return read_path, cache_path

    def set_setting(self,read_path,cache_path):
        status = 1
        logs1 = '读取路径设置完成'
        logs2 = '缓存路径设置完成'
        # 判断路径是否可用
        if not os.path.isdir(read_path):
            # 不可用则重置为""
            self.config.set('Settings','read_path','')
            read_path = ''
            logs1 = "读取路径不可用，已重置为空"
            status = 0
        cache_path2 = os.path.join(cache_path,'M_photo_cache')
        if not os.path.isdir(cache_path):
            # 不可用则重置为默认路径
            cache_path2 = BASE_CACHE_DIR
            logs2 = "缓存路径不可用，已重置为默认路径"
            status = 0
        elif os.path.exists(cache_path2):
            try:
                os.mkdir(cache_path2)
            except all:
                cache_path2 = BASE_CACHE_DIR
                logs2 = '无法创建目录，已重置为默认路径'
                status = 0
        self.config.set('Settings','read_path',read_path)
        self.config.set('Settings','cache_path',cache_path2)
        # 写入配置
        with open(self.config_path, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
        return status,logs1,logs2

    # 获取分类标签
    def get_classify(self):
        classify = self.config.get('Labels', 'classify').split(',')
        return classify
    # 设置分类标签
    def set_classify(self,classify:list[str]):
        classify = ','.join(classify)
        self.config.set('Labels', 'classify', classify)
        # 写入配置
        with open(self.config_path, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
        return 1,"分类标签设置完成"