# -*- coding:utf-8 -*-
__author__ = 'BlackIce'
import os
import fnmatch
import configparser
import shutil
from threading import Thread
import logging


def init_log():
    logger = logging.getLogger('tidy-file')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('tidy_file.log', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def all_files(root, patterns='*', single_level=False, yield_folders=False):
    """
    将模式从字符串中取出放入列表中
    :param root: 根目录
    :param patterns: 匹配的模式
    :param single_level:
    :param yield_folders:
    :return:
    """
    patterns = patterns.split(';')
    for path, sub_dirs, files in os.walk(root):
        if yield_folders:
            files.extend(sub_dirs)
        files.sort()
        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    yield os.path.join(path, name)
                    break
        if single_level:
            break


def parse_config(cfg_file='example.cfg'):
    config = configparser.RawConfigParser()
    config.read(cfg_file)
    all_sec = config.sections()
    print(all_sec)


class RootPathException(Exception):
    pass


class PathException(Exception):
    pass


class TidyFile(object):
    def __init__(self, cfg):
        self.config = configparser.RawConfigParser()
        self.config.read(cfg)
        self.all_sec = self.config.sections()
        self.p = []
        for sec in self.all_sec:
            self.p.append(Thread(target=self.tidy_sec, args=(sec,)))
        for p in self.p:
            p.start()
        # for sec in self.all_sec:
        #     self.tidy_sec(sec)

    def tidy_sec(self, sec):
        root = self.config.get(sec, 'root')
        exp = ''.join(["*.%s;" % i for i in self.config.get(sec, 'exp').strip().split(',')])
        target = self.config.get(sec, 'to')
        try:
            single_level = self.config.getboolean(sec, 'single_level')
        except configparser.NoOptionError:
            single_level = True
        if not os.path.exists(target):
            try:
                os.makedirs(target)
            except (WindowsError, IOError):
                print("create target folder fail,please check config 'to' value")

        # 目标文件夹的文件，防止重名文件覆盖
        target_folder = list(os.walk(target))
        target_files = target_folder[-1]

        for item in all_files(root, exp, single_level=single_level):
            file_name = os.path.basename(item)
            if file_name in target_files:
                new_name = os.path.basename(os.path.dirname(item))+file_name
                shutil.copy2(item, target+os.sep+new_name)
                app_log.info("%s move to %s "%(item, target+os.sep+new_name))
                target_files.append(new_name)
            shutil.copy2(item, target)
            app_log.info("%s move to %s "%(item, target))
            os.remove(item)
            # 英文中带中文的路径有bug
            # 删除空文件夹
            # folder = list(os.walk(os.path.dirname(item)))
            # if not folder[1] and not folder[2]:
            #     os.rmdir(os.path.dirname(item))
            
app_log = init_log()
app_log.info("执行开始")
TidyFile('example.cfg')
