## 2026-09-12

1. 制定计划，创建工作区，下载python，配置环境。

2. 学会了每个项目配置一个虚拟环境（python -m venv .venv）的作用和必要性。

3. 同时每次开始工作的时候都需要先在终端：.venv\Scripts\Activate.ps1 来激活虚拟环境，如果报错要记得检查脚本权限。

4. 独立项目安装依赖要在终端用：pip install -r requirements.txt

5. requirement.txt文件里可以写单行注释，安装依赖会忽略#后的内容

6. 配置项目环境可以通过右下角版本号点击，然后顶部出现选择环境，或者是命令面板搜索Python: Select Interpreter来选择。

7. 下载了适用于Windows的git环境，并安装了桌面版的git用于更方便的同步记录代码。




## 2026-09-14

1. 用：
    git config --global core.editor "notepad.exe"
    git rebase -i --root
    修改pick为reword
这些步骤来修改之前已经commit但没有push的本地仓库。 

2. plotly 库可以用于生成交互度更高的动态图片。

3. python不像C++一样区别单双引号，但是切记字符串包裹时用不一样的。

4. go.table和dict配合绘制表格的过程。

5. f-string是格式化字符串，可以用大括号来动态表示变量从而实现不同的字符串内容。

6. __pycache__文件生成的条件是：只要有一个 .py 文件被"import"过，Python 就会把它编译成字节码（.pyc），缓存在同目录下的 __pycache__ 文件夹里。
    这个文件夹可以放心删除，删了也不影响代码运行，Python 下次 import 的时候会自动重新生成。
    它本质上是一种"编译产物/缓存"，跟源代码没关系。
    不应该提交到 Git 仓库里。