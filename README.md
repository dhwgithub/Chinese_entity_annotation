# Chinese_entity_annotation

Tkinter编写的简易实体标注软件（1.0v目前仅支持Window系统）

## v2使用方法

使用方法同v1，且运行程序后会有使用说明。

相对v1对功能代码进行封装，加入了快捷键等快捷功能和增强了程序鲁棒性.

具体功能体验可在源码或运行程序后看到。



增加了文件标记功能；同时对全局常量进行了统一设置管理 -- 2020.11.4

## v1使用方法

打开txt文件，通过上一页/下一页进行当前目录的txt遍历及保存标注信息；

标注方法：通过鼠标对标注词进行左右点选（以最后两次点选为准），接着选择对应的标签即可完成标注；

生成文件：对编辑标注信息生成.txt.ann文件，同时生成可用于实体识别的BIO模型文件；

自定义设置：更改全局变量 labels_dict 可对标签进行更改（其他设置可保持不变）；

---

注意：
txt文件（和对应同名jpg文件）应放在同一目录下；

生成文件与txt文件同目录；

由于程序和文件夹存放顺序不一致（名称升序），history_info.txt文件用于记录编辑过的文件；

只适用于Win系统
    

## 运行环境:

Win 10

Python 3.7

## 直接使用

1、下载源代码

2、运行 main.py 文件即可使用

## 参考

https://github.com/jiesutd/YEDDA

https://blog.csdn.net/deex13491/article/details/101225309
