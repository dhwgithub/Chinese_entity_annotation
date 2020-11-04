# -*- coding: utf-8 -*-
"""
全局常量设置
"""
readme = '''
实体标注小程序

<方法>：
1、通过[首选项]打开指定txt文件，之后可通过上一页/下一页（或左右键）更换编辑文件，界面（展开）最右侧是当前目录剩余可编辑文件；
2、标注方法：通过鼠标对标注词进行左右点选（以最后两次点选区间为准），接着选择对应的标签即可完成标注；
3、生成标注文件：每次标注将生成.txt.ann文件，当更换到其他文件时自动保存为BIO模式文件。
4、问题文件记录：按键'Q'出现弹框，输入问题原因的编码即可记录当前文件（只有失败时才提醒）

<撤销>：
    键盘上箭头支持对本文件所有历史操作进行撤销，注意撤销操作无法反撤销且只针对当前文件。

<注意>：
1、txt文件（和对应同名jpg文件）应放在同一目录下；
2、所有生成文件与txt文件同目录，建议将编辑文件单独放于文件夹；
3、由于程序读取和文件夹存放顺序可能不一致（名称升序），history_info.txt文件用于记录编辑过的文件；
4、只适用于Windows系统，出现异常重新启动即可。

'''

# 类别标签 -> 显示名称 ： 标注字符串
# labels_dict = {
#     "商品折扣": "discount",
#     "引导行商品编码项": "goodscode",
#     "引导行商品名称项": "goodsname",
#     "引导行商品金额项": "money",
#     "引导行商品单价项": "price",
#     "引导行商品数量项": "quantity",
#     "小票号": "receiptID",
#     "零售商": "retailname",
#     "店名": "shopname",
#     "总折扣": "totaldiscount",
#     "总金额": "totalmoney",
#     "总数量": "totalquantity",
#     "交易日期": "tradedate",
#     "交易时间": "tradetime",
#     "（某个）商品编码实际值": "goodscodevalue",
#     "（某个）商品名称实际值": "goodsnamevalue",
#     "（某个）商品的其他信息": "goodsinfo"
# }
labels_dict = {
    "小票号": "receiptNo",
    "小票日期": "Date",
    "小票时间": "Time",
    "商品总数量": "totalGoodsQty",
    "商品总价": "totalMoney",
    "总优惠金额": "totalDiscountMoney",
    "零售商": "retailerName",
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
WIN_WIDTH = 1000
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
