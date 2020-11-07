# -*- coding: utf-8 -*-
"""
全局常量设置
"""
readme = '''
实体标注小程序

<方法>：
1、[首选项] --> txt文件，之后可通过上一页/下一页（或[左右键]）更换编辑文件，界面（展开）最右侧是当前目录剩余可编辑文件；
2、标注方法：通过鼠标点击指定行（红色字体行）来标注实体，接着选择对应的[标签]即可完成标注；
3、生成标注文件：每次标注完成（保存或切换到下一张）将自动生成BIO、Entity文件；
4、问题文件记录：按键'Q'出现弹框，输入问题原因对应的[编码]即可记录当前文件（只有失败时才提醒）
5、按键'H'可查看帮助

<撤销>：
    键盘[上箭头]支持对本文件所有历史操作进行回滚，注意撤销操作无法反撤销且只针对当前文件。
    
<保存>：
    ①更换其他文件编辑时自动保存；②快捷键 'H' 保存;③关闭创建自动保存当前文件

<注意>：
0、若要选择标签，请先选择标记行（重要！！！）；
1、txt文件（或对应同名jpg文件）应放在同一目录下，注意保持文件夹内无其他文件（尤其是txt文件）；
2、所有生成文件与txt文件同目录，建议将编辑文件单独放于文件夹；
3、由于程序读取和文件夹存放顺序可能不一致（名称升序），history_info.txt 文件用于记录编辑过的文件；
4、问题记录文件名为 questions_info.txt；
5、只适用于 Windows 系统。

'''

labels_dict = {
    "小票号": "receiptNo",
    "小票日期": "Date",
    "小票时间": "Time",
    "商品总数量": "totalGoodsQty",
    "商品总价": "totalMoney",
    "总优惠金额": "totalDiscountMoney",
    "零售商": "retailerName",
    "引导行的词": "startLine",
    "商品编码": "goodsCode",
    "商品数量": "goodsName",
    "单价": "goodsPrice",
    "数量": "goodsQty",
    "总价": "goodsMoney",

    "小票日期+时间": "receiptTime",
    "小票总数量和总价": "totalQM",
    "商品编码和名称": "CodeAndName",
    "商品名称后跟着价格或数量": "NameAndNum",
    "单价或数量，单价或总价相连": "priceInfo"
}

# 界面参数设置
WIN_NAME = '实体标注小程序'
WIN_WIDTH = 1270
WIN_HEIGHT = 600

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

# 图像显示缩放因子
w_box_of_img = 400
h_box_of_img = 600
