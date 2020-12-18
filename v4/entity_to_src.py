#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/17 15:10
# @Author  : Hewen Deng
# @File    : entity_to_src.py
# @Desc    : 将v3版本的实体标注软件结果转换为当前版本标注文件

import glob
import os
# from tqdm import tqdm

def get_encode_info(file):
    """
    判断文本编码并返回
    :param file: 输入文本路径
    :return:
    """
    import chardet
    with open(file, 'rb') as f:
        data = f.read()
        encoding = chardet.detect(data)
    return encoding['encoding']


def trans_file():
    """
    转换文件为当前版本可用文件
    :return:
    """
    # 获取所有文件
    file_dir = r"C:\Users\Administrator\Desktop\data"
    files_list = glob.glob(file_dir + "\*.tsv")
    # print(files_list[:5])
    # print(len(files_list))

    # 遍历每一个文件
    for file_path in files_list:
        # print(file_path)
        with open(file_path, "r", encoding=get_encode_info(file_path)) as file:
            save_temp_file = file_path[:-4] + ".temp"
            # print(save_temp_file)
            temp_file = open(save_temp_file, "w", encoding="utf-8")

            # 遍历文件的每一行信息
            for line in file.readlines():
                line = line[:-1]
                # index = line.split(",")[0]
                line = ",".join(line.split(",")[9:])
                content = ",".join(line.split(",")[:-1])
                label = line.split(",")[-1]
                # print(content, label)
                if len(content) == 0:
                    write_line = "\n"
                else:
                    if label != "other":
                        write_line = "<*{}^{}*>\n".format(content, label)
                    else:
                        write_line = "{}\n".format(content)
                # print(write_line)
                temp_file.write(write_line)

            temp_file.close()

    print("生成temp文件完成")


def save_file():
    """
    根据temp文件生成结果文件
    :return:
    """
    # 文件保存目录
    save_res_file = r"C:\Users\Administrator\Desktop\temp"
    if not os.path.exists(save_res_file):
        os.mkdir(save_res_file)

    for cur_file in glob.glob(r"C:\Users\Administrator\Desktop\temp" + "\*.temp"):
        res_file = os.path.join(save_res_file, str(cur_file).split("\\")[-1][:-5]) + ".txt"
        # print("结果文件保存位置：{}".format(res_file))
        # return

        # 格式转换与结果内容生成
        text_file = ""
        with open(cur_file, "r", encoding=get_encode_info(cur_file)) as file:
            for index, line in enumerate(file.readlines()):
                if len(line) == 1:
                    # print("跳过：{}".format(cur_file))
                    continue
                line = line[:-1]  # 标记后的单行文本
                index = index + 1  # 索引

                # 处理每一行的标签
                def __get_label_index_of_ori(line, patten):
                    """
                    从字符串line中返回一个列表
                    列表内容是line中子串是patten的下标位置列表

                    其中每个下标均为查到patten的第一个字符下标
                    :param line:
                    :param patten:
                    :return:
                    """
                    index_list = []
                    index = line.find(patten)
                    # print("查看字符串(patten为{}):{}".format(patten, line))
                    while index != -1:
                        index_list.append(index)
                        index = line.find(patten, index + len(patten))
                    return index_list

                labels = ""
                label_index_start = __get_label_index_of_ori(line, "<*")
                label_index_end = __get_label_index_of_ori(line, "*>")

                if len(label_index_start) == 0:  # 没有标签
                    labels += str(index) + " " + line + "_" + "other\n"
                else:  # 存在标签
                    index_e = -2  # 初始化第一块非标签起始位置
                    for i in range(len(label_index_start)):
                        # 处理标签中间部分（及第一个非标签部分）
                        if len(line[index_e+2: label_index_start[i]]) > 0:
                            content = line[index_e+2: label_index_start[i]]
                            labels += str(index) + " " + str(content) + "_" + "other\n"
                        # 处理标签
                        index_s = label_index_start[i]
                        index_e = label_index_end[i]
                        mini_line = line[index_s+2: index_e]  # 内容实例：2020^Date
                        content = mini_line[:mini_line.find("^")]
                        label = mini_line[mini_line.find("^")+1:]
                        labels += str(index) + " " + str(content) + "_" + str(label) + "\n"
                    if len(line[index_e+2:]) > 0:
                        labels += str(index) + " " + str(line[index_e+2:]) + "_" + "other\n"

                # 保存每个索引的所有结果
                text_file += labels

        # 保存结果文件
        with open(res_file, "w", encoding="utf-8") as file:
            file.write(text_file)


def gen_tsv_file():
    """
    生成该版本 tsv 文件
    :return:
    """
    # 获取所有文件
    file_dir = r"C:\Users\Administrator\Desktop\data"
    files_list = glob.glob(file_dir + "\*.tsv")
    # print(files_list[:5])
    # print(len(files_list))

    # 遍历每一个文件
    for file_path in files_list:
        save_path = os.path.join(r"C:\Users\Administrator\Desktop\temp", file_path.split("\\")[-1])
        save_file = open(save_path, "w", encoding="utf-8")
        # print(save_path)
        with open(file_path, "r", encoding=get_encode_info(file_path)) as file:
            for line in file.readlines():
                line = ",".join(line[:-1].split(",")[:-1])
                # print(line)
                save_file.write(line + "\n")
        save_file.close()
        # return


if __name__ == "__main__":
    # trans_file()
    # save_file()
    # gen_tsv_file()
    pass

