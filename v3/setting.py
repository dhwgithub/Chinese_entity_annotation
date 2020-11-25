# -*- coding: utf-8 -*-
"""
全局常量设置
"""
readme = '''
实体标注小程序

<常用方法>：
0、跳转文件：按'T'键并输入文件顺序编码即可跳转（历史编辑文件的编码可查看日志文件 history_info.txt）
1、[首选项] 选择编辑文件/文件夹，界面（展开）最右侧是当前目录剩余可编辑文件，最上方是当前编辑文件名
2、标注方法：通过鼠标点击行（红色字体行）来标注实体，接着选择对应的[标签]即可完成标注；
3、生成标注文件：每次标注完成（保存或切换到下一张）将自动生成BIO、Entity文件（对于同名文件优先展示编辑过的Entity文件）；
4、问题文件记录：按键'Q'出现弹框，输入问题原因对应的[编码]即可记录当前文件
5、按键'H'可查看帮助

<快捷方式>：
    左/右箭头（或Aa/Dd） 表示上一个/下一个标注文件
    上/下箭头（或Ww/Ss） 表示移动标注行
    鼠标滚轮放大缩小图像（图像区域内），或[选择]-[查看当前图像]
    B/b 表示保存标注信息（切换文件时自动保存）
    F/f 表示删除当前行标签
    T/t 表示跳转指定文件
    Q/q 表示记录问题文件
    H/h 表示查看帮助
    指定行双击鼠标左键 修改标注行

<注意>：
0、标注标签前，请先选择标记行（重要！！！）,当前标注成功后自动跳转到下一行；
1、txt文件（或对应同名jpg文件）应放在同一目录下，注意保持文件夹内无其他文件（尤其是txt文件）；
2、所有生成文件与txt文件同目录，建议将编辑文件统一放于同一文件夹；
3、history_info.txt 文件用于记录编辑过的文件信息；
4、问题记录文件名为 questions_info.txt；
5、适用于 Windows 系统。

'''
labels_dict = {
    "零售商": "retailerName",
    "小票号": "receiptNo",
    "小票日期": "Date",
    "小票时间": "Time",
    "引导行的词": "startLine",

    "商品编码": "goodsCode",
    "商品名称": "goodsName",
    "单价": "goodsPrice",
    "数量": "goodsQty",
    "总价": "goodsMoney",

    "小票总数量": "totalGoodsQty",
    "小票总价": "totalMoney",
    "总优惠金额": "totalDiscountMoney",

    "小票日期+时间": "receiptTime",
    "小票总数量和总价": "totalQM",
    "商品编码和名称": "CodeAndName",
    "商品名称+价格或数量": "NameAndNum",
    "价格信息": "priceInfo"
}
SPE_NUM_LIST = [6, 12, 16]  # 需要分割的行号（从1开始），同上分割

# 趣味功能
tag_vs_list = ["加油~", "坚持!!", "Fighting!", "Over", "试下'S'~", "继续~"]

# 界面参数设置
WIN_NAME = '实体标注小程序'
WIN_WIDTH = 1370
WIN_HEIGHT = 700

# 日志名称
LOG_FILE_NAME = 'history_info.txt'
ERROE_FILE_NAME = 'questions_info.txt'

NOT_SHOW_FILE_LIST = [LOG_FILE_NAME, ERROE_FILE_NAME]

error_dict = ['1', '2', '3']  # 与 ERROR_info 同步
ERROR_info = '''
            1:   模糊       
            2:   实体错误     
            3:   其他错误     
        '''
