import ctypes
import json
import os
import re
import sys
import sv_ttk
import dialogs
from random import choices
from tkinter import filedialog, StringVar, Tk
from tkinter.ttk import *

# 匹配的前缀
prefixes = [
    "tooltip", "displayName", "Text.yellow", "Text.of", "Text.white",
    "Text.green", "Text.gray", "Text.gold", "Text.darkPurple",
    "Text.blue", "Text.darkGreen", "Text.aqua", "Text.red", "tell"
]

# 定义存储键值对的字典
translation_dict = {}


def browseJson():
    json_var.set(
        filedialog.askopenfilename(filetypes=(('选择回填需要的json', "*.json"),), initialdir=os.path.abspath(os.path.dirname(__file__))))

def browseKubeJS():
    kubejs_var.set(
        filedialog.askdirectory(title='选择处理 KubeJS 的文件夹', initialdir=os.path.abspath(os.path.dirname(__file__))))


def on_sv_ttk_theme_select(event):
    if sv_ttk_theme_entry.get() == "亮色":
        sv_ttk.use_light_theme()
    else:
        sv_ttk.use_dark_theme()

def on_mode_select(event):
    if mode_entry.get() == "回填":
        return mode_entry.set("回填")


def gui():
    saveButton.grid_forget()
    r = 0
    json_lb.grid(row=r, column=0, pady=5, padx=20, sticky='nsew')
    json_entry.grid(row=r, column=1, pady=5, sticky='nsew')
    jsonButton.grid(row=r, column=2, pady=5, padx=30, sticky='nsew')
    r += 1
    kubejs_lb.grid(row=r, column=0, pady=5, padx=20, sticky='nsew')
    kubejs_entry.grid(row=r, column=1, pady=5, sticky='nsew')
    kubeJSButton.grid(row=r, column=2, pady=5, padx=30, sticky='nsew')
    r += 1
    mode_lb.grid(row=r, column=0, pady=5, padx=20, sticky='nsew')
    mode_entry.current(0)
    mode_entry.grid(row=r, column=1, pady=5, padx=30, sticky='nsew')
    r += 1
    sv_ttk_theme_lb.grid(row=r, column=0, pady=5, padx=20, sticky='nsew')
    sv_ttk_theme_entry.current(0)
    sv_ttk_theme_entry.grid(row=r, column=1, pady=5, padx=30, sticky='nsew')
    r += 1
    saveButton.grid(row=r, column=2, pady=5, padx=30, sticky='nsew')

    # 让列和行自适应
    for i in range(3):  # 列数
        root.columnconfigure(i, weight=1)

    for i in range(r + 1):  # 行数
        root.rowconfigure(i, weight=1)


def replace_keys_in_js(json_file, folder_path):
    with open(json_file, 'r', encoding='utf-8') as json_file:
        translation_dict = json.load(json_file)

    # 遍历文件夹里的所有.js文件
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".js"):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    js_content = file.read()

                # 遍历翻译字典，将匹配的键替换为对应的值
                for key, value in translation_dict.items():
                    js_content = js_content.replace(f'{key}', f'{value}')

                # 写回原始文件
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(js_content)
    dialogs.show_message('KubeJS翻译工具', 'KubeJS翻译工具回填翻译成功')

def runFromGui():
    if len(kubejs_var.get()) == 0 and mode_entry.get() == "提取":
        dialogs.show_message("错误", "你需要选一个文件夹。")
    elif mode_entry.get() == "提取":
        # 遍历文件夹里的所有.js文件
        for root, dirs, files in os.walk(kubejs_var.get()):
            for filename in files:
                if filename.endswith(".js"):
                    file_path = os.path.join(root, filename)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        js_content = file.read()

                    # 使用正则表达式匹配前缀并提取内容
                    for prefix in prefixes:
                        pattern = re.compile(rf'{prefix}\s*\([\'"]([^\'"]+)[\'"]\)')
                        matches = pattern.findall(js_content)
                        for match in matches:
                            # 生成随机键
                            random_key = f'kubejs.{filename[:-3]}.{"".join(choices("abcdefghijklmnopqrstuvwxyz", k=5))}'
                            # 替换匹配的内容为随机键
                            js_content = js_content.replace(f'{prefix}(\'{match}\')', f'{prefix}(\'{random_key}\')')
                            # 添加到翻译字典中
                            translation_dict[random_key] = match
                    # 写回原始文件
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(js_content)

        # 保存提取出的内容为en_us.json文件
        with open("en_us.json", 'w', encoding='utf-8') as json_file:
            json.dump(translation_dict, json_file, indent=2, ensure_ascii=False)
        dialogs.show_message('KubeJS翻译工具',
                             f'KubeJS翻译工具提取翻译成功\njson已保存在当前程序所在的文件夹中\n注意，本工具提取不全，请人工检查未提取内容')
    elif mode_entry.get() == "回填":
        replace_keys_in_js(json_var.get(), kubejs_var.get())

root = Tk()
if sys.platform == "win32":
    try:
        # >= Windows 8.1
        ScaleFactor = ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except:
        # <= Windows 8.0
        ScaleFactor = ctypes.windll.user32.SetProcessDPIAware(0)

root.title("KubeJS翻译工具 1.0")
root.iconbitmap(bitmap="icon.ico")
kubejs_var, json_var = StringVar(), StringVar()
kubejs_entry = Entry(root, textvariable=kubejs_var)
json_entry = Entry(root, textvariable=json_var)
kubejs_lb = Label(root, text="选择处理 KubeJS 的文件夹", font=10)
json_lb = Label(root, text="选择回填需要的json", font=10)
kubeJSButton = Button(root, text="选择", command=browseKubeJS)
jsonButton = Button(root, text="选择", command=browseJson)
mode_lb = Label(root, text="工作模式", font=10)
mode_list = ["提取", "回填"]
mode_entry = Combobox(root, state="readonly", values=mode_list)
mode_entry.bind("<<ComboboxSelected>>", on_mode_select)
sv_ttk.use_light_theme()
sv_ttk_theme_lb = Label(root, text="工具窗口颜色设置", font=10)
sv_ttk_theme_list = ["亮色", "暗色"]
sv_ttk_theme_entry = Combobox(root, state="readonly", values=sv_ttk_theme_list)
sv_ttk_theme_entry.bind("<<ComboboxSelected>>", on_sv_ttk_theme_select)
saveButton = Button(root, text="生成", command=runFromGui)
gui()
root.update_idletasks()
x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2) + 250
y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
root.geometry('{}x{}+{}+{}'.format(700, 300, x, y))

root.mainloop()
