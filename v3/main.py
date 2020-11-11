# -*- coding: utf-8 -*-
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
import os
from tkinter import messagebox
import time
import tkinter.font as tkFont
import random

import setting

dir_of_files = ""  # 文本所在文件夹
index_of_cur_file = 0  # 记录当前文件下标
cur_file = ""  # 当前文件
files_list_of_cur_dir = []  # 记录当前文件夹下的所有txt文本列表

show_cur_file = []  # 记录当前显示信息（不含换行符）

pre_text_by_draw = []  # 撤销，保存历次操作的下标（局部刷新）

# 记录鼠标点选位置
GET_COL = [-1, -1]  # 前闭后开
GET_ROW = [0, 0]  # 使用时行-1
pos_index = 0  # 记录鼠标点选次序

IMG_TEMP = None  # 用于持续保留图片信息
# =============================================================================


def select_file_or_dir(types):
    '''
    选择文件/文件夹
    :param types:
    :return:
    '''
    global dir_of_files, files_list_of_cur_dir, index_of_cur_file, cur_file
    index_of_cur_file = 0
    files_list_of_cur_dir = []
    f_file = True

    # 选择文件夹
    if types == 'dir_file':
        dir_of_files = tk.filedialog.askdirectory()
        for i in os.listdir(dir_of_files):
            if os.path.isfile(os.path.join(dir_of_files, i)) and os.path.join(dir_of_files, i).endswith("txt"):
                if i in setting.NOT_SHOW_FILE_LIST or i.endswith('_BIO.txt') or i.endswith('_Entity.txt'):
                    continue
                files_list_of_cur_dir.append(os.path.join(dir_of_files, i))
                if f_file:
                    f_file = False
                    cur_file = os.path.join(dir_of_files, i)
        if f_file:
            messagebox.showinfo("提示", "请检查当前文件夹是否存在标注文件！")
            return
        messagebox.showinfo("提示", "将显示第一个TXT文件！")
    # 选择文件
    elif types == 'file':
        cur_file = tk.filedialog.askopenfilename(title="打开文件")
        if cur_file in setting.NOT_SHOW_FILE_LIST or cur_file.endswith('_BIO.txt') or cur_file.endswith('_Entity.txt'):
            messagebox.showwarning("提示", "请确认文件是否正确！")
            return

        # 截取文件路径（不含文件名）
        f_split = cur_file.split('/')[:-1]
        try:
            dir_of_files = f_split[0]
        except Exception:
            messagebox.showinfo("提示", "请重新选择文件！")
            return

        for i in f_split[1:]:
            dir_of_files = dir_of_files + os.sep + i

        for i in os.listdir(dir_of_files):
            if os.path.isfile(os.path.join(dir_of_files, i)) and os.path.join(dir_of_files, i).endswith("txt"):
                if i in setting.NOT_SHOW_FILE_LIST or i.endswith('_BIO.txt') or i.endswith('_Entity.txt'):
                    continue
                files_list_of_cur_dir.append(os.path.join(dir_of_files, i))
                if i == cur_file.split('/')[-1]:
                    f_file = False
                if f_file:
                    index_of_cur_file += 1
    open_file()


def label_files_to_BIO_files(s, save_path):
    '''
    将原始标注文件转换为实体标注BIO输入文件形式
    每调用一次函数读一行
    :param s:
    :param save_path:
    :return:
    '''
    ner_data = []  # 词 标记
    id_list = [setting.labels_dict[tag] for tag in setting.labels_dict.keys()]
    if len(s) <= 18:  # 即最少也有18个字符
        return

    entity = s.split(",")[-1][:-1]
    # if entity not in id_list:
    #     # print(entity not in id_list, entity, id_list)
    #     if messagebox.askquestion("提示", "未标记内容：" + s + "\n是否继续标记当前文件？") == "yes":
    #         return False

    ok = True
    if entity in id_list:  # 标记完成
        s = s[:-len(entity)-2]  # 去除标签即原始文本行
        index = s.replace(",", ".", 7).find(",") + 1  # 实体开始的标签
        for i, b in enumerate(s):
            if i < index:
                ner_data.append((b, 'O'))
            elif i == index:
                ner_data.append((b, 'B-' + entity))
            else:
                ner_data.append((b, 'I-' + entity))
    else:  # 未完成标记
        ok = False
        for b in s:
            ner_data.append((b, 'O'))

    # 保存
    f = open(save_path, 'a', encoding='utf-8')
    for each in ner_data:
        ans = each[0] + ' ' + str(each[1])
        flag = True
        if ans[0] == '\n' and ans[2] == 'O':
            ans = '\n'
            flag = False
        f.write(ans)
        if flag:
            f.write('\n')
    f.write('\n')
    f.close()
    return ok


def save_file():
    '''
    保存标注文件
    :return:
    '''
    global text_model, cur_file, pre_text_by_draw, index_of_cur_file
    if len(pre_text_by_draw) <= 1:
        return

    f = open(setting.LOG_FILE_NAME, 'a', encoding='utf-8')
    f.write('编辑文件：' + cur_file + ' ' + str(index_of_cur_file + 1) + '\n')
    f.close()

    # 保存编辑文件
    edit_file = cur_file.split(".")[0] + "_Entity.txt"
    if edit_file.split("_")[-2] == 'Entity':  # 读取的是 Entity 文件，进一步表示该编辑文件不用再修改了
        edit_file = cur_file

        f = open(edit_file, 'w', encoding='utf-8')
        text_content = text_model.get("0.0", "end").split("\n")
        text_content.pop()
        tf = open(cur_file[:-11] + ".txt", 'r', encoding=get_encode_info(cur_file[:-11] + ".txt"))
        tf = tf.read().split("\n")
        texts = ""
        i = 0
        for line in text_content:
            if len(tf) <= i or len(tf[i]) <= 8:
                continue
            t = tf[i].split(",")[:8]
            t = ",".join(t)
            texts += t + "," + line + "\n"
            i += 1
        f.write(texts)
        f.close()
    else:
        f = open(edit_file, 'w', encoding='utf-8')
        text_content = text_model.get("0.0", "end").split("\n")
        text_content.pop()
        tf = open(cur_file, 'r', encoding=get_encode_info(cur_file))
        tf = tf.read().split("\n")
        texts = ""
        i = 0
        for line in text_content:
            if len(tf) <= i or len(tf[i]) <= 8:
                continue
            t = tf[i].split(",")[:8]
            t = ",".join(t)
            texts += t + "," + line + "\n"
            i += 1
        f.write(texts)
        f.close()

    # 生成BIO文件
    f = open(edit_file, 'r', encoding='utf-8')
    save_path = edit_file[:-11] + '_BIO.txt'

    if save_path.split("_")[-2] == 'Entity':  # 读取的是 Entity 文件
        save_path = cur_file[:-11] + '_BIO.txt'

    if os.path.exists(save_path):
        os.remove(save_path)

    ok = True
    SUM = 0
    for s in f.readlines():
        t_ok = label_files_to_BIO_files(s, save_path)
        if t_ok is False:
            SUM += 1
            ok = False
    if not ok:
        f = open(setting.LOG_FILE_NAME, 'a', encoding='utf-8')
        if save_path.endswith('_BIO.txt'):
            save_path = save_path[:-8] + "_Entity.txt"
        f.write(save_path + "\n==>>> 存在" + str(SUM) + "个/行标注不完全情况（详情请查看前述文件内容）\n")
        f.close()


def show_last_file():
    '''
    显示上一个文本
    :return:
    '''
    global index_of_cur_file, cur_file, files_list_of_cur_dir
    save_file()
    # print('当前文件: %s' % index_of_cur_file)
    if index_of_cur_file - 1 < 0:
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
    if index_of_cur_file + 1 >= len(files_list_of_cur_dir):
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
    :param cur_file:
    :return:
    '''
    global frame_pic, IMG_TEMP
    pic_path = cur_file.split('.')[0] + '.jpg'

    load = Image.open(pic_path)
    w, h = load.size
    load = resize_img(w, h, setting.w_box_of_img, setting.h_box_of_img, load)
    IMG_TEMP = ImageTk.PhotoImage(load)
    tk.Label(frame_pic, image=IMG_TEMP, width=setting.w_box_of_img, height=setting.h_box_of_img).pack()


def btn_ok(event):
    '''
    记录鼠标点击坐标
    :param event:
    :return:
    '''
    global text_model, GET_COL, GET_ROW, pos_index

    text_model.tag_delete("tag")

    cursor_index = text_model.index('insert')
    row_column = cursor_index.split('.')
    # GET_COL[pos_index] = row_column[-1]
    GET_ROW[pos_index] = row_column[0]

    rec = str(GET_ROW[pos_index]) + ".0"
    rec2 = str(int(GET_ROW[pos_index]) + 1) + ".0"
    text_model.tag_add('tag', rec, rec2)  # 申明一个tag,在a位置使用
    text_model.tag_config('tag', foreground='red')  # 设置tag即插入文字的大小,颜色等

    # print(GET_ROW[0])
    # if pos_index == 0:
    #     pos_index = 1
    # else:
    #     pos_index = 0


def get_encode_info(file):
    """
    判断文本编码
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
    global text_model, pre_text_by_draw, index_of_cur_file, files_list_of_cur_dir, frame_pic, show_cur_file, cur_file
    global dir_of_files
    try:
        pre_text_by_draw = []

        # cur_file 有_Entity
        old_cur_file = cur_file.split(".")[0] + "_Entity.txt"
        files_of_dir = os.listdir(dir_of_files)
        use_entity = False
        if old_cur_file.split("/")[-1] in files_of_dir or old_cur_file.split("\\")[-1] in files_of_dir:
            cur_file = old_cur_file
            use_entity = True

        files = open(cur_file, 'r', encoding=get_encode_info(cur_file))
        texts = files.read()
        files.close()

        # 设置显示的文本信息
        show_cur_file = []
        for line in texts.split("\n"):
            show_cur_file.append(",".join(line.split(",")[8:]))

        text_model.config(state=tk.NORMAL)
        text_model.delete(0.0, tk.END)
        show_cur_file_draw = ""
        for line in show_cur_file:
            show_cur_file_draw += line + "\n"
            text_model.insert('end', line + "\n")
        text_model.config(state=tk.DISABLED)
        pre_text_by_draw.append(-1)

        # 显示列表
        get_contents_list(files_list_of_cur_dir[index_of_cur_file:], txt_list)

        try:
            for widget in frame_pic.winfo_children():  # 清空图片
                widget.destroy()
            t = cur_file
            if use_entity:
                t = t[:-11] + ".txt"
            show_picture(str(t))
        except Exception:
            tk.Label(frame_pic, text='暂\n无\n图\n片\n显\n示').pack()
            pass
        temp_str = '已完成：%d / %d' % ((index_of_cur_file + 1), len(files_list_of_cur_dir))
        temp_str += "\t" + setting.tag_vs_list[random.randint(0, len(setting.tag_vs_list)-1)]
        tip.set(temp_str)

        # 获取鼠标
        text_model.bind("<ButtonRelease-1>", btn_ok)
    except Exception:
        text_model.config(state=tk.NORMAL)
        text_model.delete(0.0, tk.END)
        text_model.insert('end', 'error file')
        text_model.config(state=tk.DISABLED)
        messagebox.showerror("错误", "文件打开错误！")


def key_board(event):
    '''
    获取按键并处理
    :param event:
    :return:
    '''
    global text_model
    if event.keysym == 'Right':
        show_next_file()
    elif event.keysym == 'Left':
        show_last_file()
    elif event.keysym == 'Up':
        global pre_text_by_draw
        if len(pre_text_by_draw) <= 1:
            return
        # 获取上次操作的原文件信息
        index = int(pre_text_by_draw.pop())  # 获取上次操作行号
        row = text_model.get(str(index) + ".0", str(index + 1) + ".0")[:-1]
        row = ",".join(row.split(",")[:-1])

        text_model.config(state=tk.NORMAL)
        text_model.delete(str(index) + ".0", str(index + 1) + ".0")
        text_model.insert(str(index) + ".0", row + "\n")
        text_model.config(state=tk.DISABLED)
    elif event.keysym == 'Q':
        global cur_file
        from tkinter import simpledialog

        t_cur_file = cur_file
        if t_cur_file[-10:].split(".")[0] == 'Entity':
            t_cur_file = t_cur_file[:-11] + ".txt"

        error_info = simpledialog.askstring('请输入错误编码', setting.ERROR_info)

        f = open(setting.LOG_FILE_NAME, 'a', encoding='utf-8')
        f.write('记录问题文件：' + t_cur_file + ' ---> ')

        if error_info in setting.error_dict:
            error_file = open(setting.ERROE_FILE_NAME, 'a', encoding='utf-8')
            if '\\' in t_cur_file:
                temp = t_cur_file.split('\\')[-1]
            else:
                temp = t_cur_file.split('/')[-1]
            error_file.write('%s %s\n' % (temp, error_info))
            error_file.close()

            f.write('%s\n' % error_info)
            messagebox.showinfo("提示", "记录成功！")
        else:
            f.write('记录失败\n')
            messagebox.showwarning("错误", "编码输入错误！")

        f.close()
    elif event.keysym == "S" or event.keysym == "Down":
        save_file()
        messagebox.showinfo("提示", "保存成功！")
    elif event.keysym == "H":
        messagebox.showinfo("帮助", setting.readme)
    elif event.keysym == "T":
        show_want_file()


def add_label(k):
    '''
    通过按钮来对选中文本添加标签
    :param k:
    :return:
    '''
    global text_model, GET_COL, GET_ROW
    if cur_file == "":
        return

    # 获取标注词并更改为标注后的信息
    r0 = int(GET_ROW[0])  # 从1开始

    cur_line = text_model.get(str(r0) + '.0', str(r0 + 1) + '.0')[:-1]

    # 如果之前有标签则替换
    last_len = len(cur_line)
    if cur_line.split(",")[-1] in [k for i, k in setting.labels_dict.items()]:
        cur_line = cur_line[:-len(cur_line.split(",")[-1]) - 1]
    text_model.config(state=tk.NORMAL)
    text_model.delete(str(r0) + "." + str(len(cur_line)), str(r0) + "." + str(last_len))
    text_model.config(state=tk.DISABLED)

    # 插入新标签
    LEN = int(len(cur_line))
    LEN = str(r0) + "." + str(LEN)
    text_model.config(state=tk.NORMAL)
    text_model.insert(LEN, "," + setting.labels_dict[k])
    # print(t)
    text_model.config(state=tk.DISABLED)

    # 获取当前文本信息
    text_content = text_model.get("0.0", "end").split("\n")
    text_content.pop()  # 列表最后一个元素是空删除它

    # texts = ""
    # for rows in text_content:
    #     texts += rows + "\n"
    # texts = texts[:-1]

    # pre_text_by_draw.append(texts)
    pre_text_by_draw.append(r0)

    # 自动显红下一行
    GET_ROW[0] = int(GET_ROW[0]) + 1
    text_model.tag_delete("tag")
    rec = str(GET_ROW[pos_index]) + ".0"
    rec2 = str(int(GET_ROW[pos_index]) + 1) + ".0"
    text_model.tag_add('tag', rec, rec2)  # 申明一个tag,在a位置使用
    text_model.tag_config('tag', foreground='red')  # 设置tag即插入文字的大小,颜色等


def get_contents_list(file_list, txt_list):
    '''
    显示目录列表
    :param file_list:
    :return:
    '''
    txt_list.config(state=tk.NORMAL)
    txt_list.delete(0.0, tk.END)
    for file_path in file_list:
        txt_list.insert('end', file_path.split('\\')[-1] + '\n\n')
    txt_list.config(state=tk.DISABLED)


def main():
    '''主界面'''
    window = tk.Tk()
    window.title(setting.WIN_NAME)
    window.geometry('%dx%d' % (setting.WIN_WIDTH, setting.WIN_HEIGHT))

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

    '''日志记录'''
    f = open(setting.LOG_FILE_NAME, 'a', encoding='utf-8')
    f.write('==================  ' + time.asctime(time.localtime(time.time())) + '==================\n')
    f.close()

    '''错误文件记录初始化'''
    # e = open(setting.ERROE_FILE_NAME, 'a', encoding='utf-8')
    # e.write('==================  ' + time.asctime(time.localtime(time.time())) + '==================\n')
    # e.close()

    '''完成文件计数器'''
    global tip
    tip = tk.StringVar()
    tk.Entry(frame_label, textvariable=tip, font=15, width=24, bg='#F0F0F0', relief=tk.FLAT).pack(pady=10)

    '''目录设置'''
    menubar = tk.Menu(window)

    m1 = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='首选项', menu=m1)
    m1.add_command(label='打开TXT文件', command=lambda: select_file_or_dir('file'))
    m1.add_command(label='打开文件夹', command=lambda: select_file_or_dir('dir_file'))

    m2 = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='选择', menu=m2)
    m2.add_command(label='上一张 & 保存', command=show_last_file)
    m2.add_separator()    # 添加一条分隔线
    m2.add_command(label='下一张 & 保存', command=show_next_file)

    '''文本组件设置'''
    global text_model
    ft = tkFont.Font(size=18, weight=tkFont.BOLD)
    text_model = tk.Text(frame_text, height=100, font=ft, width=50, bd=2)

    scroll = tk.Scrollbar()
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    scroll.config(command=text_model.yview)

    text_model.config(yscrollcommand=scroll.set, state=tk.DISABLED)
    text_model.config(state=tk.NORMAL)
    text_model.insert('end', '请选择txt文件/文件夹\n\n(按"H"键查看帮助)')
    text_model.config(state=tk.DISABLED)
    text_model.pack(padx=5, pady=20)

    '''标签显示与设置'''
    for i in setting.labels_dict:
        tk.Button(frame_label, text=i, font=12, anchor='center', pady=2, bg="white", relief=tk.GROOVE,
                  width=24, command=lambda i=i: add_label(i)).pack()

    '''目录列表展示'''
    global txt_list
    ft2 = tkFont.Font(size=12, weight=tkFont.NORMAL)
    txt_list = tk.Text(frame_list, height=100, font=ft2, width=300, bd=2, bg='#F0F0F0', relief=tk.FLAT)

    scroll2 = tk.Scrollbar()
    scroll2.pack(side=tk.RIGHT, fill=tk.Y)
    scroll2.config(command=txt_list.yview)

    txt_list.config(yscrollcommand=scroll2.set)
    txt_list.insert('end', setting.readme)
    txt_list.config(state=tk.DISABLED)
    txt_list.pack(padx=20, pady=30)

    '''界面绑定设置'''
    window.bind("<Key>", key_board)
    window.config(menu=menubar)  # 将目录放入窗口中

    window.mainloop()


if __name__ == '__main__':
    main()
'''
pyinstaller -F -w -i favicon.ico -p D:\Anaconda\envs\temp_py\Lib\site-packages main.py
'''
