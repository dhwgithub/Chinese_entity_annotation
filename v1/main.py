import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
import os
from tkinter import messagebox
import time
'''
实体标注小程序

打开txt文件，通过上一页/下一页进行当前目录的txt遍历及保存标注信息
标注方法：通过鼠标对标注词进行左右点选（以最后两次点选为准），接着选择对应的标签即可完成标注
生成文件：对编辑标注信息生成.txt.ann文件，同时生成可用于实体识别的BIO模型文件

自定义设置：更改全局变量 labels_dict 可对标签进行更改（其他设置可保持不变）
注意：txt文件（和对应同名jpg文件）应放在同一目录下；
    生成文件与txt文件同目录；
    由于程序和文件夹存放顺序不一致（名称升序），history_info.txt文件用于记录编辑过的文件；
    只适用于Win系统
    
运行环境:
Win 10
Python 3.7
'''
window = tk.Tk()
window.title('中文实体标注')
window.geometry('1000x600')

f = open('history_info.txt', 'a', encoding='utf-8')
f.write('==================  ' + time.asctime(time.localtime(time.time())) + '==================\n')
f.close()

'''
主界面
'''
frame = tk.Frame(window).pack()

frame_pic = tk.Frame(frame)
frame_text = tk.Frame(frame)
frame_label = tk.Frame(frame)
frame_pic.pack(side="left")
frame_text.pack(side="left")
frame_label.pack(side="left")

'''
全局变量
'''
FILE_PATH = ""  # 文本所在文件夹
file_index = 0  # 记录当前文件下标
cur_file = ""  # 当前文件
FILE_LIST = []  # 记录当前文件夹下的所有txt文本列表

w_box = 400
h_box = 600

tip = tk.StringVar()
tk.Entry(frame_label, textvariable=tip, font=15).pack()

labels_dict = {"商品折扣": "discount",
               "引导行商品编码项": "goodscode",
               "引导行商品名称项": "goodsname",
               "引导行商品金额项": "money",
               "引导行商品单价项": "price",
               "引导行商品数量项": "quantity",
               "小票号": "receiptID",
               "零售商": "retailname",
               "店名": "shopname",
               "总折扣": "totaldiscount",
               "总金额": "totalmoney",
               "总数量": "totalquantity",
               "交易日期": "tradedate",
               "交易时间": "tradetime",
               "（某个）商品编码实际值": "goodscodevalue",
               "（某个）商品名称实际值": "goodsnamevalue",
               "（某个）商品的其他信息": "goodsinfo"
}

'''
目录设置
'''


def select():
    global FILE_PATH, FILE_LIST, file_index, cur_file
    cur_file = tk.filedialog.askopenfilename(title="打开文件")

    f_split = cur_file.split('/')[:-1]
    try:
        FILE_PATH = f_split[0]
    except Exception:
        messagebox.showinfo("提示", "没有选择任何文本，请重新选择！")
        return

    for i in f_split[1:]:
        FILE_PATH = FILE_PATH + os.sep + i

    f_file = True
    for i in os.listdir(FILE_PATH):
        if os.path.isfile(os.path.join(FILE_PATH, i)) and os.path.join(FILE_PATH, i).endswith("txt"):
            if i == 'history_info.txt' or i.endswith('.txt.ann') or i.endswith('_EntryName.txt'):
                continue
            FILE_LIST.append(os.path.join(FILE_PATH, i))
            print(i, cur_file.split('/')[-1])
            if i == cur_file.split('/')[-1]:
                f_file = False
            if f_file:
                file_index += 1

    print(FILE_LIST)
    print("下标：", file_index)
    open_file()


def str2ner_train_data(s, save_path):
    '''
    将原始标注文件转换为实体标注输入文件形式
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
        print('错误标注')
        return
    assert len(begin) == len(end)
    i = 0
    j = 0
    while i < len(s):
        if i not in begin:
            # print(s[i])
            ner_data.append([s[i], 'O'])
            i = i + 1
        else:
            ann = s[i + 2:end[j] - 2]
            entity, ner = ann.rsplit('#')
            if (len(entity) == 1):
                ner_data.append([entity, 'S-' + ner])
            else:
                if (len(entity) == 2):
                    ner_data.append([entity[0], 'B-' + ner])
                    ner_data.append([entity[1], 'I-' + ner])
                else:
                    ner_data.append([entity[0], 'B-' + ner])
                    for n in range(1, len(entity)):
                        ner_data.append([entity[n], 'I-' + ner])
                    # ner_data.append([entity[-1], 'E-' + ner])

            i = end[j]
            j = j + 1

    f = open(save_path, 'a', encoding='utf-8')
    for each in ner_data:
        # if str(each[1]) == 'O':
        #     print(each[0])
        ans = each[0] + ' ' + str(each[1])
        flag = True
        if ans[0] == '\n' and ans[2] == 'O':
            ans = '\n'
            flag = False
        #     continue
        #     print(ans, len(ans), '.'+ans[0]+'.', '.'+ans[1]+'.', '.'+ans[2]+'.')
        f.write(ans)
        if flag:
            f.write('\n')
    f.close()


def save_text():
    global edit_file
    f = open('history_info.txt', 'a', encoding='utf-8')
    f.write('编辑文件：' + cur_file + '\n')
    f.close()

    # TODO 真正保存标注信息，需要保存的是edit_file信息，同时将其转换为标注文件
    if edit_file == "":
        # messagebox.showinfo("提示", "当前文件并没有进行编辑操作！")
        return
    f = open(edit_file, 'r', encoding='utf-8')
    save_path = edit_file[:-8] + '_EntryName.txt'

    for s in f.readlines():
        str2ner_train_data(s, save_path)

    # f = open(save_path, 'r', encoding='utf-8')
    # pre_str = "tip"


def show_last():
    global file_index, cur_file, FILE_LIST, edit_file
    save_text()
    if file_index - 1 < 0:
        messagebox.showinfo("提示", "已经是第一张了~")
        return
    edit_file = ""
    file_index -= 1
    print("下标：", file_index)
    cur_file = FILE_LIST[file_index]
    open_file()


def show_next():
    global file_index, cur_file, FILE_LIST, edit_file
    save_text()
    if file_index + 1 >= len(FILE_LIST):
        messagebox.showinfo("提示", "已经是最后一张了~")
        return
    edit_file = ""
    file_index += 1
    print("下标：", file_index)
    cur_file = FILE_LIST[file_index]
    open_file()


menubar = tk.Menu(window)
m1 = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='首选项', menu=m1)
m1.add_command(label='添加文本文件', command=select)

m2 = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='选择', menu=m2)
m2.add_command(label='上一张 & 保存', command=show_last)
m2.add_separator()    # 添加一条分隔线
m2.add_command(label='下一张 & 保存', command=show_next)


'''
显示图片界面
'''


def resize(w, h, w_box, h_box, pil_image):
    '''
    resize a pil_image object so it will fit into
    a box of size w_box times h_box, but retain aspect ratio
    对一个pil_image对象进行缩放，让它在一个矩形框内，还能保持比例
    '''
    f1 = 1.0*w_box/w # 1.0 forces float division in Python2
    f2 = 1.0*h_box/h
    factor = min([f1, f2])
    #print(f1, f2, factor) # test
    # use best down-sizing filter
    width = int(w*factor)
    height = int(h*factor)
    return pil_image.resize((width, height), Image.ANTIALIAS)


render = None


def get_pic(cur_file):
    global frame_pic, render
    pic_path = cur_file.split('.')[0] + '.jpg'
    # print('图片路径：', pic_path)

    load = Image.open(pic_path)
    w, h = load.size
    load = resize(w, h, w_box, h_box, load)
    render = ImageTk.PhotoImage(load)
    tk.Label(frame_pic, image=render, width=w_box, height=h_box).pack()


'''
显示文本界面
'''
GET_COL = [-1, -1]  # 前闭后开
GET_ROW = [-1, -1]  # 使用时行-1
pos_index = 0


def btn_ok(event):
    global t, GET_COL, GET_ROW, pos_index
    cursor_index = t.index('insert')
    row_column = cursor_index.split('.')
    # cursor_text = ("row: %s   col: %s" % (row_column[0], row_column[-1]))
    GET_COL[pos_index] = row_column[-1]
    GET_ROW[pos_index] = row_column[0]
    if pos_index == 0:
        pos_index = 1
    else:
        pos_index = 0
    # print('start:', cursor_text)
    # print(GET_ROW)
    # print(GET_COL)

# def btn_up(event):
#     global t
#     cursor_index = t.index('insert')
#     row_column = cursor_index.split('.')
#     cursor_text = ("row: %s   col: %s" % (row_column[0], row_column[-1]))
#     print('end:', cursor_text)


def open_file():
    try:
        global t
        print("当前文件：", cur_file)
        # show_txt = cur_file
        files = open(cur_file, 'r', encoding='utf-8')
        texts = files.read()
        files.close()

        t.delete(0.0, tk.END)
        t.insert('end', texts)

        for widget in frame_pic.winfo_children():  # 清空图片
            widget.destroy()
        get_pic(str(cur_file))
        tip.set(cur_file)

        # # 获取鼠标
        t.bind("<ButtonRelease-1>", btn_ok)
        t.tag_configure('highlight', background="green", foreground="black")
    except Exception:
        t.delete(0.0, tk.END)
        t.insert('end', 'error file')


t = tk.Text(frame_text, height='400', font=17, width=50)

scroll = tk.Scrollbar()
# 放到窗口的右侧, 填充Y竖直方向
scroll.pack(side=tk.RIGHT, fill=tk.Y)
# 两个控件关联
scroll.config(command=t.yview)
t.config(yscrollcommand=scroll.set)
t.insert('end', '请选择txt文件')
t.pack()


'''
显示标签 和 按钮
'''
edit_file = ""  # 当前编辑文本，仅在更换文本时更新，后续操作都在此编辑


def add_label(k):
    '''
    通过按钮来修改文本标注
    :param k:
    :return:
    '''
    global edit_file, t, GET_COL, GET_ROW
    if cur_file == "":
        return

    # print('cur_label:', labels_dict[k])

    # TODO 获取当前文本信息
    # text_content = []  # 用来储存每一行内容的列表
    text_content = t.get("0.0", "end").split("\n")
    text_content.pop()  # 列表最后一个元素是空删除它
    print(text_content)
    # print(len(text_content))

    # TODO 获取标注词并更改为标注后的信息
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
        print('标注词: ', entry)
        text_content[r0-1] = text_content[r0-1][:c0] + \
                             '[@' + entry + '#' + labels_dict[k] + '*]' + text_content[r0-1][c1:]
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
            # print('中间过程temp：', temp)
            entry += temp
            row_num += 1
        print('标注词: ', entry)
        text_content[r0-1] = text_content[r0-1][:c0] + '[@' + entry + '#' + labels_dict[k] + '*]'

        add_num = 0
        del_rows = r1 - 1 - r0
        # print('需要删除行数：', del_rows)
        for row_num in range(r0, r1-1):  # 删除中间的多余行，即属于标注词的部分
            # print('需要删除的行号：', row_num)
            row_num = row_num - add_num
            add_num += 1
            text_content = text_content[:row_num] + text_content[row_num+1:]
        # print('最后一行:', r1-1-del_rows)
        text_content[r1-1-del_rows] = text_content[r1-1-del_rows][c1:]

    if entry == "":
        return

    # print(text_content)
    texts = ""
    for rows in text_content:
        texts += rows + "\n"
    texts = texts[:-1]
    # print(texts)
    # TODO 更新文本信息+写入edit_file文件+显示更新结果
    t.delete(0.0, tk.END)
    t.insert('end', texts)

    edit_file = cur_file + '.ann'
    f = open(edit_file, 'w', encoding='utf-8')
    f.write(texts)
    f.close()


for i in labels_dict:
    # label = tk.Label(frame_label, text=i, font=15, anchor='center').pack()
    bn = tk.Button(frame_label, text=i, font=17, anchor='center', pady=2, bg="white",
                   command=lambda i=i: add_label(i)).pack()
    # label = labels_dict[i]
    # print(label)


window.config(menu=menubar)  # 将目录放入窗口中
window.mainloop()
