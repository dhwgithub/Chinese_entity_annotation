# -*- coding: utf-8 -*-
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
import os
from tkinter import messagebox
import time
import tkinter.font as tkFont

import setting

dir_of_files = ""  # 文本所在文件夹
index_of_cur_file = 0  # 记录当前文件下标
cur_file = ""  # 当前文件
files_list_of_cur_dir = []  # 记录当前文件夹下的所有txt文本列表

edit_file = ""  # 当前编辑文本，仅在更换文本时更新，后续操作都在此编辑

pre_text_by_draw = []  # 撤销

# 记录鼠标点选位置
GET_COL = [-1, -1]  # 前闭后开
GET_ROW = [-1, -1]  # 使用时行-1
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
                if i in setting.NOT_SHOW_FILE_LIST or i.endswith('.txt.ann') or i.endswith('_EntryName.txt'):
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
        if cur_file in setting.NOT_SHOW_FILE_LIST or cur_file.endswith('.txt.ann') or cur_file.endswith('_EntryName.txt'):
            messagebox.showinfo("提示", "文件类型有误！")
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
                if i in setting.NOT_SHOW_FILE_LIST or i.endswith('.txt.ann') or i.endswith('_EntryName.txt'):
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
    :param s:
    :param save_path:
    :return:
    '''
    import re
    ner_data = []
    result_1 = re.finditer(r'\[\@', s)
    result_2 = re.finditer(r'\*\]', s)
    begin = []
    end = []
    for each in result_1:
        begin.append(each.start())
    for each in result_2:
        end.append(each.end())
    if len(begin) != len(end):
        messagebox.showerror("提示", "出现未知异常！")
        return
    assert len(begin) == len(end)
    i = 0
    j = 0
    while i < len(s):
        if i not in begin:
            ner_data.append([s[i], 'O'])
            i = i + 1
        else:
            ann = s[i + 2:end[j] - 2]
            entity, ner = ann.rsplit('#')
            if (len(entity) == 1):
                ner_data.append([entity, 'S-' + ner])
            else:
                if len(entity) == 2:
                    ner_data.append([entity[0], 'B-' + ner])
                    ner_data.append([entity[1], 'I-' + ner])
                else:
                    ner_data.append([entity[0], 'B-' + ner])
                    for n in range(1, len(entity)):
                        ner_data.append([entity[n], 'I-' + ner])

            i = end[j]
            j = j + 1

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
    f.close()


def save_file():
    '''
    保存标注文件
    :return:
    '''
    global edit_file
    f = open(setting.LOG_FILE_NAME, 'a', encoding='utf-8')
    f.write('编辑文件：' + cur_file + '\n')
    f.close()

    # 真正保存标注信息，需要保存的是edit_file信息，同时将其转换为标注文件
    if edit_file == "":
        # messagebox.showinfo("提示", "当前文件并没有进行编辑操作！")
        return
    f = open(edit_file, 'r', encoding='utf-8')
    save_path = edit_file[:-8] + '_EntryName.txt'

    if os.path.exists(save_path):
        os.remove(save_path)
    for s in f.readlines():
        label_files_to_BIO_files(s, save_path)


def show_last_file():
    '''
    显示上一个文本
    :return:
    '''
    global index_of_cur_file, cur_file, files_list_of_cur_dir, edit_file
    save_file()
    if index_of_cur_file - 1 < 0:
        messagebox.showinfo("提示", "已经是第一张了~")
        return
    edit_file = ""
    index_of_cur_file -= 1
    cur_file = files_list_of_cur_dir[index_of_cur_file]
    open_file()


def show_next_file():
    '''
    显示下一个文本
    :return:
    '''
    global index_of_cur_file, cur_file, files_list_of_cur_dir, edit_file
    save_file()
    if index_of_cur_file + 1 >= len(files_list_of_cur_dir):
        messagebox.showinfo("提示", "已经是最后一张了~")
        return
    edit_file = ""
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
    cursor_index = text_model.index('insert')
    row_column = cursor_index.split('.')
    GET_COL[pos_index] = row_column[-1]
    GET_ROW[pos_index] = row_column[0]
    if pos_index == 0:
        pos_index = 1
    else:
        pos_index = 0


def open_file():
    '''
    打开文件等一系列相关操作
    :return:
    '''
    try:
        global text_model, pre_text_by_draw, index_of_cur_file, files_list_of_cur_dir, frame_pic
        pre_text_by_draw = []

        files = open(cur_file, 'r', encoding='utf-8')
        texts = files.read()
        files.close()

        text_model.delete(0.0, tk.END)
        text_model.insert('end', texts)
        pre_text_by_draw.append(texts)

        # 显示列表
        get_contents_list(files_list_of_cur_dir[index_of_cur_file:], txt_list)

        try:
            for widget in frame_pic.winfo_children():  # 清空图片
                widget.destroy()
            show_picture(str(cur_file))
        except Exception:
            tk.Label(frame_pic, text='暂\n无\n图\n片\n显\n示').pack()
            pass
        # print('======================================')
        temp_str = '已完成：%d / %d' % ((index_of_cur_file + 1), len(files_list_of_cur_dir))
        tip.set(temp_str)

        # 获取鼠标
        text_model.bind("<ButtonRelease-1>", btn_ok)
    except Exception:
        text_model.delete(0.0, tk.END)
        text_model.insert('end', 'error file')
        messagebox.showerror("错误", "文件打开错误！")


def key_board(event):
    '''
    获取按键并处理
    :param event:
    :return:
    '''
    # print(event.keysym)
    if event.keysym == 'Right':
        show_next_file()
    elif event.keysym == 'Left':
        show_last_file()
    elif event.keysym == 'Up':
        global pre_text_by_draw
        if len(pre_text_by_draw) <= 1:
            return
        pre_text_by_draw.pop()  # 删除当前信息
        text_model.delete(0.0, tk.END)
        text_model.insert('end', pre_text_by_draw[-1])
    elif event.keysym == 'Q':
        global cur_file
        from tkinter import simpledialog
        error_info = simpledialog.askstring('请输入错误编码', setting.ERROR_info)

        f = open(setting.LOG_FILE_NAME, 'a', encoding='utf-8')
        f.write('记录问题文件：' + cur_file + ' ---> ')

        if error_info in setting.error_dict:
            error_file = open(setting.ERROE_FILE_NAME, 'a', encoding='utf-8')
            if '\\' in cur_file:
                temp = cur_file.split('\\')[-1]
            else:
                temp = cur_file.split('/')[-1]
            error_file.write('%s %s\n' % (temp, error_info))
            error_file.close()

            f.write('%s\n' % error_info)
            messagebox.showinfo("提示", "记录成功！")
        else:
            f.write('记录失败\n')
            messagebox.showwarning("错误", "编码输入错误！")

        f.close()
    else:
        if len(pre_text_by_draw) == 0:
            return
        text_content = text_model.get("0.0", "end").split("\n")
        if pre_text_by_draw[-1] != text_content:
            text_model.delete(0.0, tk.END)
            text_model.insert('end', pre_text_by_draw[-1])


def add_label(k):
    '''
    通过按钮来对选中文本添加标签
    :param k:
    :return:
    '''
    global edit_file, text_model, GET_COL, GET_ROW
    if cur_file == "":
        return

    # 获取当前文本信息
    text_content = text_model.get("0.0", "end").split("\n")
    text_content.pop()  # 列表最后一个元素是空删除它

    # 获取标注词并更改为标注后的信息
    r0 = int(GET_ROW[0])
    r1 = int(GET_ROW[1])
    c0 = int(GET_COL[0])
    c1 = int(GET_COL[1])

    if r0 == -1 or r1 == -1 or c0 == -1 or c1 == -1 or (r0 == r1 and c0 == c1):
        return

    if r0 == r1:  # 同一行
        if c0 > c1:
            temp = c0
            c0 = c1
            c1 = temp
        entry = text_content[r0-1][c0: c1]  # 标注词
        # print('标注词: ', entry)
        text_content[r0-1] = text_content[r0-1][:c0] + \
                             '[@' + entry + '#' + setting.labels_dict[k] + '*]' + text_content[r0-1][c1:]
    else:
        if r0 > r1:  # 顺序排列
            temp = r0
            r0 = r1
            r1 = temp
            temp = c0
            c0 = c1
            c1 = temp
        entry = ""
        row_num = r0 - 1  # 起始行
        for rows in text_content[r0-1: r1]:
            temp = ""
            if row_num == r0 - 1:  # 第一行
                for c in rows[c0:]:
                    temp += c
            elif row_num == r1 - 1:  # 最后一行
                for c in rows[:c1]:
                    temp += c
            else:
                temp += rows
            entry += temp
            row_num += 1

        if entry.startswith('[@') and entry.endswith('*]'):
            messagebox.showinfo("提示", "标注过多！")
            return
        # print('标注词: ', entry)
        text_content[r0-1] = text_content[r0-1][:c0] + '[@' + entry + '#' + setting.labels_dict[k] + '*]'

        add_num = 0
        del_rows = r1 - 1 - r0
        # print('需要删除行数：', del_rows)
        for row_num in range(r0, r1-1):  # 删除中间的多余行，即属于标注词的部分
            # print('需要删除的行号：', row_num)
            row_num = row_num - add_num
            add_num += 1
            text_content = text_content[:row_num] + text_content[row_num+1:]
        try:
            text_content[r1-1-del_rows] = text_content[r1-1-del_rows][c1:]
        except Exception:
            messagebox.showinfo("提示", "操作有误！")
            return

    if entry == "":
        return

    GET_ROW[0] = -1
    GET_ROW[1] = -1
    GET_COL[0] = -1
    GET_COL[1] = -1

    # print(text_content)
    texts = ""
    for rows in text_content:
        texts += rows + "\n"
    texts = texts[:-1]
    # print(texts)
    # 更新文本信息+写入edit_file文件+显示更新结果
    text_model.delete(0.0, tk.END)
    text_model.insert('end', texts)

    pre_text_by_draw.append(texts)

    edit_file = cur_file + '.ann'
    f = open(edit_file, 'w', encoding='utf-8')
    f.write(texts)
    f.close()


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

    '''错误文件记录'''
    e = open(setting.ERROE_FILE_NAME, 'a', encoding='utf-8')
    e.write('==================  ' + time.asctime(time.localtime(time.time())) + '==================\n')
    e.close()

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
    text_model = tk.Text(frame_text, height=100, font=ft, width=28, bd=2)

    scroll = tk.Scrollbar()
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    scroll.config(command=text_model.yview)

    text_model.config(yscrollcommand=scroll.set)
    text_model.insert('end', '请选择txt文件')
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
