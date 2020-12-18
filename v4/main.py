# -*- coding: utf-8 -*-
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
import os
from tkinter import messagebox
import time
import tkinter.font as tkFont
import random
import threading
from tkinter import simpledialog
from natsort import natsorted
import glob

import setting


# 窗口大小
global win_width, win_height

# 组件
global frame_pic, text_model, txt_list

# 监听相关
global is_valid_range  # 是否是合法范围，即用来标记划词的第一列
global cur_line_num, cur_line_start, cur_line_end  # 划词行号、开始列、结束列

# 文件相关：路径分割统一是 \\
global dir_of_files  # 文件夹路径
global cur_file  # 当前文件路径
global files_list_of_cur_dir  # 所有文件路径列表
global index_of_cur_file  # 当前文件下标（上述列表）
global is_modified  # 标记是否对文件进行修改
global origin_cur_file  # 上一次保存的文件路径（每次优先加载）

# 图片相关
global IMG_TEMP  # 保存当前图像对象（同时保证不会图像显示时丢失）
global add_w, add_h  # 图像缩放单元


# =============================================================================
def init_var():
    """
    变量初始化
    :return:
    """
    global cur_line_num, cur_line_start, cur_line_end, origin_cur_file, index_of_cur_file
    cur_line_num = -1
    cur_line_start = -1
    cur_line_end = -1

    origin_cur_file = None
    index_of_cur_file = None


def select_file_or_dir(types):
    '''
    选择文件/文件夹

    只能选择以 .tsv 结尾的文件/文件夹
    :param types:
    :return:
    '''
    global dir_of_files, files_list_of_cur_dir, index_of_cur_file, cur_file, text_model

    # 选择文件夹
    if types == 'dir_file':
        dir_of_files = tk.filedialog.askdirectory()
        dir_of_files = "\\".join(dir_of_files.split("/"))
        # print("文件夹路径:{}".format(dir_of_files))

        # 获取所有文件
        files_list_of_cur_dir = natsorted(glob.glob(dir_of_files + '\*.tsv'))
        if len(files_list_of_cur_dir) == 0:
            messagebox.showinfo("提示", "当前文件夹内无标注文件！")
            text_model.config(state=tk.NORMAL)
            text_model.delete(0.0, tk.END)
            text_model.insert('end', '\n\t请重新选择文件\n\n\t"H"键查看帮助')
            text_model.config(state=tk.DISABLED)
            return

        # 设置当前文件
        cur_file = files_list_of_cur_dir[0]
        # print("当前文件：{}".format(cur_file))
        index_of_cur_file = 0

    # 选择文件
    elif types == 'file':
        # 文件路径
        cur_file_temp = tk.filedialog.askopenfilename(title="打开文件")

        # 没有选择文件
        if len(cur_file_temp) == 0:
            return

        cur_file = r'\\'.join(cur_file_temp.split('/'))
        if not cur_file.endswith('.tsv'):
            messagebox.showinfo("提示", "文件类型有误，请重新选择！")
            text_model.config(state=tk.NORMAL)
            text_model.delete(0.0, tk.END)
            text_model.insert('end', '\n\t请重新选择文件\n\n\t"H"键查看帮助')
            text_model.config(state=tk.DISABLED)
            return

        # 文件夹路径
        dir_of_files = '\\'.join(cur_file.split(r'\\')[:-1])
        print("文件夹路径:{}".format(dir_of_files))

        # 获取所有文件
        files_list_of_cur_dir = natsorted(glob.glob(dir_of_files + '\*.tsv'))

        # 获取当前文件下标
        index_of_cur_file = files_list_of_cur_dir.index(str(cur_file_temp).replace('/', '\\', 100))

    open_file()


def get_label_index_of_ori(line, patten):
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


def save_file():
    '''
    保存标注文件

    保存文本内容格式：index text_label
    :return:
    '''
    global is_modified, origin_cur_file, dir_of_files, cur_file

    # 没有做任何修改
    if origin_cur_file is None or not is_modified:
        return

    # 文件保存目录
    res_file = os.path.join(dir_of_files, str(cur_file).split("\\")[-1][:-4] + ".txt")
    # print("结果文件保存位置：{}".format(res_file))

    # 格式转换与结果内容生成
    text_file = ""
    with open(origin_cur_file, "r", encoding=get_encode_info(origin_cur_file)) as file:
        for index, line in enumerate(file.readlines()):
            if len(line) == 1:
                continue
            line = line[:-1]  # 标记后的单行文本
            index = index + 1  # 索引

            # 处理每一行的标签
            labels = ""
            label_index_start = get_label_index_of_ori(line, "<*")
            label_index_end = get_label_index_of_ori(line, "*>")

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


def show_last_file():
    '''
    显示上一个文本
    :return:
    '''
    global index_of_cur_file, cur_file, files_list_of_cur_dir
    save_file()
    # print('当前文件: %s' % index_of_cur_file)
    if index_of_cur_file is None or index_of_cur_file - 1 < 0:
        messagebox.showinfo("提示", "已经是第一张了~")
        return
    index_of_cur_file -= 1
    cur_file = files_list_of_cur_dir[index_of_cur_file]
    open_file()


def show_want_file():
    '''
    显示指定文件（需要输入顺序编码）
    :return:
    '''
    global index_of_cur_file, cur_file, files_list_of_cur_dir

    try:
        from tkinter import simpledialog
        id = int(simpledialog.askstring('文件跳转', '\n--- 请输入跳转文件编码 ---\n'))

        save_file()
        index_of_cur_file = id - 1
        cur_file = files_list_of_cur_dir[index_of_cur_file]
        open_file()
    except Exception:
        messagebox.showinfo('提示', '文件编码输入有误！')


def show_next_file():
    '''
    显示下一个文本
    :return:
    '''
    global index_of_cur_file, cur_file, files_list_of_cur_dir
    save_file()
    if index_of_cur_file is None or index_of_cur_file + 1 >= len(files_list_of_cur_dir):
        messagebox.showinfo("提示", "已经是最后一张了~")
        return
    index_of_cur_file += 1
    cur_file = files_list_of_cur_dir[index_of_cur_file]
    open_file()


def resize_img(w, h, w_box, h_box, pil_image):
    '''
    对一个pil_image对象进行缩放，让它在一个矩形框内，还能保持比例
    '''
    f1 = 1.0 * w_box / w
    f2 = 1.0 * h_box / h
    factor = min([f1, f2])
    width = int(w * factor)
    height = int(h * factor)
    return pil_image.resize((width, height), Image.ANTIALIAS)


def show_picture(cur_file):
    '''
    显示图片
    :return:
    '''
    global frame_pic, IMG_TEMP, win_width, win_height
    pic_path = cur_file.split('.')[0] + '.jpg'

    load = Image.open(pic_path)
    w, h = load.size
    load = resize_img(w, h, int(0.36496 * win_width), win_height, load)
    IMG_TEMP = ImageTk.PhotoImage(load)
    temp = tk.Label(frame_pic, image=IMG_TEMP, width=int(0.36496 * win_width), height=win_height)
    temp.bind("<MouseWheel>", call_back)
    temp.pack()


def call_back(event):
    """
    鼠标滚轮控制图像大小
    :param event:
    :return:
    """
    global frame_pic, IMG_TEMP, cur_file, add_w, add_h, win_width, win_height

    for widget in frame_pic.winfo_children():  # 清空图片
        widget.destroy()
    pic_path = cur_file.split('.')[0] + '.jpg'

    load = Image.open(pic_path)
    w, h = load.size
    if event.delta > 0 and add_h <= 2500:
        add_w += 50
        add_h += 50
    elif add_h >= 300 and add_w > 50:
        add_w -= 50
        add_h -= 50
    load = resize_img(w, h, add_w, add_h, load)
    IMG_TEMP = ImageTk.PhotoImage(load)
    temp = tk.Label(frame_pic, image=IMG_TEMP, width=int(0.36496 * win_width), height=win_height)
    temp.bind("<MouseWheel>", call_back)
    temp.pack()


def cancel_label(event):
    """
    双击取消标记
    :param event:
    :return:
    """
    global text_model, cur_line_num, cur_line_start, cur_line_end
    text_model.tag_delete("tag")
    cur_line_num = -1
    cur_line_start = -1
    cur_line_end = -1


def mouse_press(event):
    """
    记录鼠标被按下的行列
    :param event:
    :return:
    """
    global text_model, is_valid_range
    text_model.tag_delete("tag")
    is_valid_range = False


def mouse_release(event):
    """
    监听鼠标松开（主要用于逆方向划词的矫正）
    :param event:
    :return:
    """
    global text_model, cur_line_start, cur_line_end, cur_line_num
    text_model.tag_delete("tag")

    if int(cur_line_start) > int(cur_line_end):
        cur_line_start = int(cur_line_start) ^ int(cur_line_end)
        cur_line_end = int(cur_line_end) ^ int(cur_line_start)
        cur_line_start = int(cur_line_start) ^ int(cur_line_end)
    # print(cur_line_start, cur_line_end)

    rec = str(cur_line_num) + "." + str(cur_line_start)
    rec2 = str(cur_line_num) + "." + str(cur_line_end)
    text_model.tag_add('tag', rec, rec2)  # 申明一个tag,在a位置使用
    text_model.tag_config('tag', foreground='red')  # 设置tag即插入文字的大小,颜色等


def mouse_move(event):
    """
    对鼠标划词进行显示和标注
    :param event:
    :return:
    """
    global text_model, cur_line_num, cur_line_start, cur_line_end, is_valid_range
    text_model.tag_delete("tag")

    cursor_index = text_model.index('insert')
    row_column = cursor_index.split('.')

    # 刚开始划词
    if not is_valid_range:
        cur_line_num = row_column[0]
        cur_line_start = row_column[1]
        is_valid_range = True

    cur_line_end = row_column[1]

    # print("双击获取标签利用：{}行{}列".format(row_column[0], row_column[1]))

    # 倒序划词显示设置（最后配合鼠标松开监听）
    cur_line_start_temp = int(cur_line_start)
    cur_line_end_temp = int(cur_line_end)
    if cur_line_start_temp > cur_line_end_temp:
        cur_line_start_temp = cur_line_start_temp ^ cur_line_end_temp
        cur_line_end_temp = cur_line_end_temp ^ cur_line_start_temp
        cur_line_start_temp = cur_line_start_temp ^ cur_line_end_temp

    rec = str(cur_line_num) + "." + str(cur_line_start_temp)
    rec2 = str(cur_line_num) + "." + str(cur_line_end_temp)
    # print("划词有效位置：{}--{}".format(rec, rec2))
    text_model.tag_add('tag', rec, rec2)  # 申明一个tag,在a位置使用
    text_model.tag_config('tag', foreground='red')  # 设置tag即插入文字的大小,颜色等


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


def open_file():
    '''
    打开文件等一系列相关操作
    :return:
    '''
    global text_model, origin_cur_file, is_modified, cur_file, frame_pic
    global win_width, win_height, add_w, add_h
    global index_of_cur_file, files_list_of_cur_dir, is_modified

    try:
        # 初始化为未修改信息
        is_modified = False

        # 所有文件操作都写入 modify_cur_file 文件
        # print("当前文件路径：{}".format(cur_file))
        origin_cur_file = cur_file.split(".")[0] + ".temp"
        # print("编辑文件位置：{}".format(origin_cur_file))

        # 获取原始文件所有文字信息并显示（若存在历史文件则优先加载历史文件）
        show_cur_file = []
        if os.path.exists(origin_cur_file):  # 存在历史文件
            files = open(origin_cur_file, 'r', encoding=get_encode_info(origin_cur_file))
            texts = files.read()
            files.close()

            for line in texts.split("\n"):
                show_cur_file.append(line)
        else:
            files = open(cur_file, 'r', encoding=get_encode_info(cur_file))
            texts = files.read()
            files.close()

            for line in texts.split("\n"):
                show_cur_file.append(",".join(line.split(",")[9:]))

        # 显示文本信息
        text_model.config(state=tk.NORMAL)
        text_model.delete(0.0, tk.END)
        for line in show_cur_file:
            text_model.insert('end', line + "\n")
        text_model.config(state=tk.DISABLED)

        # 添加标签颜色
        if os.path.exists(origin_cur_file):
            add_label_color()

        # # 字体颜色测试
        # text_model.tag_add("test", "1.0", "1.3")
        # text_model.tag_config("test", foreground="olive")

        # 显示右侧目录列表
        get_contents_list()

        # 显示对于图片
        try:
            # 清空图片
            for widget in frame_pic.winfo_children():
                widget.destroy()

            add_w = int(win_width * 0.36496)
            add_h = win_height
            show_picture(str(cur_file))
        except Exception:
            tk.Label(frame_pic, text='暂\n无\n图\n片\n显\n示').pack()

        # 设置进度提示标签
        temp_str = '已完成：%d / %d' % ((index_of_cur_file + 1), len(files_list_of_cur_dir))
        temp_str += "\t" + setting.tag_vs_list[random.randint(0, len(setting.tag_vs_list) - 1)]
        tip.set(temp_str)
    except Exception:
        text_model.config(state=tk.NORMAL)
        text_model.delete(0.0, tk.END)
        text_model.insert('end', 'error file')
        text_model.config(state=tk.DISABLED)
        messagebox.showerror("错误", "文件打开异常！")


def delete_label():
    """
    通过划词删除标签
    :return:
    """
    global text_model, is_modified, cur_line_num, cur_line_end, cur_line_start, origin_cur_file

    # 获取选中行信息
    pos_temp = ["{}.0".format(cur_line_num), "{}.0".format(int(cur_line_num) + 1)]
    cur_line = text_model.get(pos_temp[0], pos_temp[1])[:-1]

    # 判断是否有标签
    index_start = get_label_index_of_ori(cur_line, "<*")
    index_end = get_label_index_of_ori(cur_line, "*>")
    exists_label = False
    if len(index_start) == 0:
        messagebox.showinfo("提示", "请正确选择想要删除的标签~")
        return
    for index in range(len(index_start)):
        l = int(index_start[index])
        r = int(index_end[index]) + 1
        # print(l, r, cur_line[l: r + 1])

        if (l <= int(cur_line_start) <= r) and (l <= int(cur_line_end) - 1 <= r):
            exists_label = True
            break

    if not exists_label:
        messagebox.showinfo("提示", "请正确选择想要删除的标签~")
        return

    # 获取选中标签信息
    start = int(str(cur_line[:int(cur_line_end)]).rfind("<*"))
    end = int(str(cur_line[int(cur_line_end):]).find("*>")) + len(str(cur_line[:int(cur_line_end)]))
    # print("len(cur_line):{}\tstart:{}\tend:{}".format(len(cur_line), start, end))
    cur_label_all = cur_line[start + 2: end]
    # print("选择标签: {}".format(cur_label_all))
    content = cur_label_all[:int(str(cur_label_all).find("^"))]  # 选中文本
    label = cur_label_all[int(str(cur_label_all).find("^")) + 1:]  # 选择标签值
    # print("content: {}\tlabel：{}".format(content, label))

    # 删除标签颜色对象
    try:
        text_model.tag_delete("{}_{}".format(content, label))
    except Exception:
        print("删除标签颜色失败:{},{}".format(content, label))

    # 删除标签
    modify_cur_line = cur_line[:start] + str(content) + cur_line[end + 2:]
    text_model.config(state=tk.NORMAL)
    text_model.delete(str(cur_line_num) + ".0", str(cur_line_num) + "." + str(len(cur_line)))
    text_model.insert(str(cur_line_num) + ".0", modify_cur_line)
    text_model.config(state=tk.DISABLED)

    # 为当前行标签添加颜色
    add_label_color(cur_line_num)

    # 更新 origin_cur_file 文件
    # 1、修改状态
    is_modified = True
    cur_line_num = -1
    cur_line_end = -1
    cur_line_start = -1

    # 2、获取当前界面信息
    cur_text_info = str(text_model.get("0.0", "end"))

    # 3、修改编辑文本并保存
    with open(origin_cur_file, "w", encoding=get_encode_info(origin_cur_file)) as file:
        for line in cur_text_info.split("\n"):
            if len(line) == 0:
                break
            file.write(line + "\n")


def key_board(event):
    '''
    获取按键并处理
    :param event:
    :return:
    '''
    global text_model
    if event.keysym == 'Right' or event.keysym == 'd' or event.keysym == 'D':  # 下一张
        show_next_file()
    elif event.keysym == 'Left' or event.keysym == 'a' or event.keysym == 'A':  # 上一张
        show_last_file()
    elif event.keysym == "S" or event.keysym == "s":  # 保存
        save_file()
        messagebox.showinfo("提示", "保存成功！")
    elif event.keysym == "H" or event.keysym == "h":
        messagebox.showinfo("帮助", setting.readme)
    elif event.keysym == "T" or event.keysym == "t":  # 跳转文件
        show_want_file()
    elif event.keysym == "Delete":  # 删除标签
        delete_label()


def add_label_color(all_line=-1):
    """
    为标签添加颜色
    默认全部染色，否则传入指定行数染色
    :return:
    """
    global text_model

    cur_text_info = str(text_model.get("0.0", "end"))
    for l_num, line in enumerate(cur_text_info.split("\n")):
        if len(line) == 0:
            continue
        l_num += 1  # 行号

        # 非所有行都重新染色，指定行染色
        if all_line != -1 and int(all_line) != l_num:
            continue

        # 对每行的标签进行处理
        start_index = get_label_index_of_ori(line, "<*")
        end_index = get_label_index_of_ori(line, "*>")
        for index in range(len(start_index)):
            rec = str(l_num) + "." + str(start_index[index])
            rec2 = str(l_num) + "." + str(int(end_index[index]) + 2)
            content_and_label = line[int(str(start_index[index]))+2: int(end_index[index])].split("^")
            text_model.tag_add("{}_{}".format(content_and_label[0], content_and_label[1]), rec, rec2)
            text_model.tag_config("{}_{}".format(content_and_label[0], content_and_label[1]),
                                  foreground=setting.label_color[random.randint(0, len(setting.label_color) - 1)])


def add_label(k):
    '''
    通过按钮来对选中文本添加标签
    :param k:
    :return:
    '''
    global text_model, is_modified, cur_line_num, cur_line_start, cur_line_end
    global origin_cur_file

    # 无效添加标签
    if int(cur_line_start) == int(cur_line_end):
        return
    if origin_cur_file is None:
        messagebox.showinfo("提示", "请选择文件")
        return
    # print(cur_line_num, cur_line_start, cur_line_end)

    # 获取行信息
    pos_temp = ["{}.0".format(cur_line_num), "{}.0".format(int(cur_line_num) + 1)]
    cur_line = text_model.get(pos_temp[0], pos_temp[1])[:-1]
    # print("cur_line: {}".format(cur_line))

    # 获取并添加标签信息
    cur_label = cur_line[int(cur_line_start): int(cur_line_end)]
    # print("cur_label: {}".format(cur_label))
    content = str(cur_label)
    label = setting.labels_dict[k]
    # print("content: {}\tlabel: {}".format(content, label))

    # 标签嵌套重叠判断 并 替换标签
    index_start = get_label_index_of_ori(cur_line, "<*")
    index_end = get_label_index_of_ori(cur_line, "*>")
    modify_label_num = 0
    modify_cur_line = ""
    for index in range(len(index_start)):
        l = int(index_start[index])
        r = int(index_end[index]) + 1
        # print(l, r, cur_line[l: r + 1])

        # 计算标签重叠数
        if (l <= int(cur_line_start) <= r) or (l <= int(cur_line_end) - 1 <= r) or \
                (int(cur_line_start) <= l <= int(cur_line_end) - 1) or \
                (int(cur_line_start) <= r <= int(cur_line_end) - 1):
            modify_label_num += 1

        # 修改重叠的标签，若多个则返回
        if (l <= int(cur_line_start) <= r) and (l <= int(cur_line_end) - 1 <= r):
            # 获取重叠标签左右下标（左闭右开区间）
            # print(cur_line[l: r + 1])  # 得到当前标签信息<*请^Time*>
            content = str(cur_line[l: r + 1][2: -2]).split("^")[0]
            # print("content:{}".format(content))
            modify_cur_line = cur_line[:l] \
                              + "<*{}^{}*>".format(content, label) \
                              + cur_line[r + 1:]

    # 添加标签
    if modify_label_num == 0:
        modify_cur_line = cur_line[:int(cur_line_start)] \
                          + "<*{}^{}*>".format(content, label) \
                          + cur_line[int(cur_line_end):]
    elif modify_label_num >= 1 and modify_cur_line == "":
        messagebox.showinfo("提示", "请选择一个标签进行修改")
        return

    # print("modify_cur_line:{}".format(modify_cur_line))

    # 在界面删除当前行信息并添加新内容
    text_model.config(state=tk.NORMAL)
    text_model.delete(str(cur_line_num) + ".0", str(cur_line_num) + "." + str(len(cur_line)))
    text_model.insert(str(cur_line_num) + ".0", modify_cur_line)
    text_model.config(state=tk.DISABLED)

    # 为当前行标签添加颜色
    add_label_color(cur_line_num)

    # 保存入编辑文件中（每次仅保留最新界面呈现效果）
    restore_info = text_model.get("0.0", "end")[:-1]
    # print(restore_info)
    with open(origin_cur_file, "w", encoding="utf-8") as ori_file:
        ori_file.write(restore_info)

    # 修改状态
    is_modified = True
    cur_line_start = -1
    cur_line_end = -1
    cur_line_num = -1


def get_contents_list():
    """
    显示目录列表，且当前文件位于第一个位置
    :return:
    """
    global txt_list, files_list_of_cur_dir, index_of_cur_file

    txt_list.config(state=tk.NORMAL)
    txt_list.delete(0.0, tk.END)
    for file_path in files_list_of_cur_dir[index_of_cur_file:]:
        txt_list.insert('end', file_path.split('\\')[-1] + '\n\n')
    txt_list.config(state=tk.DISABLED)


class ThreadClass(threading.Thread):
    """
    开启图像显示线程
    """
    def __init__(self, pic_path):
        super(ThreadClass, self).__init__()
        self.pic_path = pic_path

    def run(self):
        im = Image.open(self.pic_path)
        im.show()


def get_cur_img():
    """
    打开自带图片查看器
    :return:
    """
    global cur_file
    try:
        pic_path = cur_file.split('.')[0] + '.jpg'

        t = ThreadClass(pic_path)
        t.start()
    except Exception:
        messagebox.showinfo("提示", "当前图片不存在")
        return


def main():
    # 变量初始化
    init_var()

    '''主界面'''
    window = tk.Tk()

    # 根据屏幕分辨率调节窗口大小
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    percentage_width = .72
    percentage_height = .65

    # 实际窗口大小
    global win_width, win_height
    win_width = int(percentage_width * screen_width)
    win_height = int(percentage_height * screen_height)

    window.title(setting.WIN_NAME)
    window.geometry('%dx%d' % (win_width, win_height))

    '''界面组件'''
    global frame_pic
    frame = tk.Frame(window).pack()

    frame_pic = tk.Frame(frame)
    frame_text = tk.Frame(frame)
    frame_label = tk.Frame(frame)
    frame_list = tk.Frame(frame)

    frame_pic.pack(side="left")
    frame_text.pack(side="left")
    frame_label.pack(side="left")
    frame_list.pack(side="left")

    # '''日志记录'''
    # f = open(setting.LOG_FILE_NAME, 'a', encoding='utf-8')
    # f.write('==================  ' + time.asctime(time.localtime(time.time())) + '==================\n')
    # f.close()

    '''完成文件计数器'''
    global tip
    tip = tk.StringVar()
    tk.Entry(frame_label, textvariable=tip, font=15, width=int(0.01605839 * win_width),
             bg='#F0F0F0', relief=tk.FLAT).pack(pady=8)

    '''目录设置'''
    menubar = tk.Menu(window)

    m1 = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='首选项', menu=m1)
    m1.add_command(label='打开文件', command=lambda: select_file_or_dir('file'))
    m1.add_command(label='打开文件夹', command=lambda: select_file_or_dir('dir_file'))

    m2 = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='选择', menu=m2)
    m2.add_command(label='上一张 & 保存', command=show_last_file)
    m2.add_separator()  # 添加一条分隔线
    m2.add_command(label='下一张 & 保存', command=show_next_file)
    m2.add_separator()  # 添加一条分隔线
    m2.add_command(label='查看当前图像', command=get_cur_img)

    '''文本组件设置'''
    global text_model
    ft = tkFont.Font(size=18, weight=tkFont.BOLD)
    text_model = tk.Text(frame_text, height=int(0.1429 * win_height), font=ft, width=int(0.035 * win_width), bd=2,
                         bg='#C7EDCC')
    # 墨绿 #C7EDCC  淡黄 #FAF9DE

    text_model.config(state=tk.NORMAL)
    text_model.insert('end', '\n\t请选择txt文件/文件夹\n\n\t(按"H"键查看帮助)')
    text_model.config(state=tk.DISABLED)
    text_model.pack(padx=5, pady=20)

    '''标签显示与设置'''
    num = 1
    for i in setting.labels_dict:
        # 分割行
        if num in setting.SPE_NUM_LIST:
            num += 1
            tk.Label(frame_label, text="     ").pack()
        num += 1
        # 标签
        tk.Button(frame_label, text=i, font=12, anchor='center', pady=2, bg="white", relief=tk.GROOVE,
                  width=int(0.018 * win_width), command=lambda i=i: add_label(i)).pack()

    '''目录列表展示'''
    global txt_list
    ft2 = tkFont.Font(size=12, weight=tkFont.NORMAL)
    txt_list = tk.Text(frame_list, height=int(0.1429 * win_height), font=ft2, width=int(0.2190 * win_width), bd=2,
                       bg='#F0F0F0', relief=tk.FLAT)

    txt_list.insert('end', setting.readme)
    txt_list.config(state=tk.DISABLED)
    txt_list.pack(padx=20, pady=30)

    """鼠标监听设置"""
    # 监听鼠标划词范围
    text_model.bind("<ButtonPress-1>", mouse_press)  # 监听按下鼠标左键
    text_model.bind("<B1-Motion>", mouse_move)  # 监听鼠标移动
    text_model.bind("<ButtonRelease-1>", mouse_release)  # 监听鼠标松开

    '''按键绑定设置'''
    window.bind("<Key>", key_board)
    window.bind("<Double-Button-1>", cancel_label)

    window.config(menu=menubar)  # 将目录放入窗口中
    window.mainloop()


if __name__ == '__main__':
    main()
'''
pyinstaller -F -w -i favicon.ico -p D:\Anaconda\envs\temp_py\Lib\site-packages main.py
'''
