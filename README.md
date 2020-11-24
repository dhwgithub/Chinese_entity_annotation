# Chinese_entity_annotation

Tkinter 编写的简易实体标注软件（目前仅支持Window系统）

## v3使用方法（最新版）

在前两个版本的基础上对操作方式和功能等进行了较大改变，同时对原标记文件进行了适应性调整。更多信息参考使用说明书！

**主要功能如下：**

```data
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

```

**界面展示：**

![1604731038941](https://github.com/dhwgithub/Chinese_entity_annotation/blob/main/img/1604731038941.png)

**操作页面：**
![1604731322373](https://github.com/dhwgithub/Chinese_entity_annotation/blob/main/img/1604731322373.png)

其中从坐到右分别是对应图片展示区、文本显示区（无法输入）、标签区（含标记进度）、文本列表区（第一行始终是当前文本名称）。

通过鼠标点击指定行则显示为红色，之后可以点击右侧标签进行标注（图中已标记）。之后可以通过快捷键或选项切换编辑文件，同时可以进行当前文件所有操作的回滚和保存当前文件标注信息。

**操作完成后：**

会生成以 _Entity.txt 和 _BIO.txt 文件，前者是对应文本框的原始标注文件（如果存在则优先显示该文件支持继续编辑），后者是对应标注信息的BIO模式文件；

同时生成 history_info.txt 的历史操作文件，记录编辑过的文件以及标记没有完成的文件信息（含日期），还有 questions_info.txt 记录问题文件，表示该文件有问题，需要其他处理才能标注（含文件名及对应设置的代号）

**直接使用：**

- 体验版（原版）：

直接运行 ```EntityAnnotation.exe``` 即可。

- 需要修改配置时：

对于标签，可直接修改 setting.py 文件中的 labels_dict 变量即可（显示名：标注名）

对于原标注文件，根据内容对 show_cur_file（文本框显示）、error_dict（错误编码）、ERROR_info（错误字典且与error_dict对应）等进行修改。具体流程从读入文件以及添加标签进行修改。

—— 2020.11.7

**更新日志：**

- 对 _Entity.txt 文件优先编辑，不需要像原v3版本一样手动修改文件名才能继续编辑（现在用户完全无需关心该问题），优化了标注体验。——2020.11.8
- 增加趣味小功能，在进度显示后面随机展示简短激励性短语（需要提前设置好内容）。——2020.11.8
- 实现兼容其他编码格式的txt文件。——2020.11.8
- 支持修改指定标签（解决撤销多次的麻烦）、自动显红下一行（提高标注效率）。——2020.11.9
- 增加文件跳转 + 修复不紧要的bug。——2020.11.11
- 取消撤销功能，添加删除标签功能、双击修改标注文本功能、使用本地图像查看工具功能、添加更多快捷键功能等，修复bug，如多种分辨率显示问题。——2020.11.24

*更多信息请参考使用说明书，欢迎提出宝贵意见！！！*

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
    

## 源码运行环境:

altgraph==0.17
certifi==2020.6.20
chardet==3.0.4
future==0.18.2
pefile==2019.4.18
Pillow==8.0.1
pyinstaller==4.0
pyinstaller-hooks-contrib==2020.10
pywin32-ctypes==0.2.0
wincertstore==0.2

## v1版本参考

https://github.com/jiesutd/YEDDA

https://blog.csdn.net/deex13491/article/details/101225309
