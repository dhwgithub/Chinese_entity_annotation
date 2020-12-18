# -*- coding: utf-8 -*-
"""
全局常量设置
"""
readme = '''
实体标注小程序

<常用方法>：
0、跳转文件：按'T'键并输入文件顺序编码即可跳转
1、[首选项] 选择编辑文件/文件夹，界面（展开）最右侧是当前目录剩余可编辑文件，最上方是当前编辑文件名
2、标注方法：通过鼠标滑动区间（红色字体行），接着选择对应的[标签]即可完成标注；
3、生成标注文件：每次标注完成（保存或切换到下一张）将自动编辑文件，用于加载历史操作，可手动删除；
4、在标注区间内部分滑动并按键'M'可修改标签，输入数字表示右侧标签（删除数字表示删除标签）
5、按键'H'可查看帮助

<快捷方式>：
    左/右箭头（或Aa/Dd） 表示上一个/下一个文件
    鼠标滚轮放大缩小图像（图像区域内），或[选择]-[查看当前图像]
    M/m 表示修改标注信息（首先要选择修改的标签）
    T/t 表示跳转指定文件
    S/s 表示保存文件
    H/h 表示查看帮助
    双击鼠标左键 取消当前红色行标记

<注意>：
0、修改标签前，请先选择要修改的标签（删除数字表示删除标签）；
1、编辑过程会生成历史编辑文件，用于加载之前的操作（可手动删除重新标注）；
2、标注结果文件位于当前目录的[result]文件夹内；
3、适用于 Windows 系统。

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

# 修改标签提示信息
modify_tag_info = """
    [不输入任何数字表示删除标签]
    
    "零售商": 1
    "小票号": 2
    "小票日期": 3
    "小票时间": 4
    "引导行的词": 5

    "商品编码": 6
    "商品名称": 7
    "单价": 8
    "数量": 9
    "总价": 10

    "小票总数量": 11
    "小票总价": 12
    "总优惠金额": 13

    "小票日期+时间": 14
    "小票总数量和总价": 15
    "商品编码和名称": 16
    "商品名称+价格或数量": 17
    "价格信息": 18
"""

# 标签颜色
label_color = ["red", "blue", "green",
               "yellow", "gray", "purple",
               "navy", "olive"]

# 趣味功能
tag_vs_list = ["加油~", "坚持!!", "Fighting!", "记得保存", "继续~"]

# 界面参数设置
WIN_NAME = '实体标注小程序'
WIN_WIDTH = 1370
WIN_HEIGHT = 700

# # 日志名称
# LOG_FILE_NAME = 'history_info.txt'