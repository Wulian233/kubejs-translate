import ctypes
import json
import os
import re
import sys
import time
import sv_ttk
import glob
import dialogs
from random import choices
from tkinter import filedialog, StringVar, BooleanVar, Tk
from tkinter.ttk import *

# 匹配的前缀
prefixes = [
    "displayName", "tooltip", "tell", "Text.yellow", "Text.of",
    "Text.white", "Text.green", "Text.gray", "Text.gold", "Text.darkPurple",
    "Text.blue", "Text.darkGreen", "Text.aqua", "Text.red"
]

# 定义存储键值对的字典
translation_dict = {}


def browseJson():
    json_var.set(
        filedialog.askopenfilename(filetypes=(('选择 json 语言文件', "*.json"),),
                                   initialdir=os.path.abspath(os.path.dirname(__file__))))


def browseKubeJS():
    kubejs_var.set(
        filedialog.askdirectory(title='选择处理 KubeJS 的文件夹',
                                initialdir=os.path.abspath(os.path.dirname(__file__))))


def on_mode_select(event):
    if mode_entry.get() == '回填':
        return mode_entry.set('回填')


def gui():
    saveButton.grid_forget()
    r = 1
    json_lb.grid(row=r, column=0, pady=5, padx=20, sticky='nsew')
    json_entry.grid(row=r, column=1, pady=5, sticky='nsew')
    jsonButton.grid(row=r, column=2, pady=5, padx=30, sticky='nsew')
    r += 1
    kubejs_lb.grid(row=r, column=0, pady=5, padx=20, sticky='nsew')
    kubejs_entry.grid(row=r, column=1, pady=5, sticky='nsew')
    kubeJSButton.grid(row=r, column=2, pady=5, padx=30, sticky='nsew')
    r += 2
    mode_lb.grid(row=r, column=0, pady=5, padx=20, sticky='nsew')
    mode_entry.current(0)
    mode_entry.grid(row=r, column=1, pady=5, padx=30, sticky='nsew')
    sv_ttk_theme.grid(row=r, column=2, pady=5, padx=30, sticky='nsew')
    r += 1
    replaceButton.grid(row=r, column=1, pady=5, padx=30, sticky='nsew')
    saveButton.grid(row=r, column=2, pady=5, padx=30, sticky='nsew')

    # 让列和行自适应
    for i in range(3):  # 列数
        root.columnconfigure(i, weight=1)

    for i in range(r + 1):  # 行数
        root.rowconfigure(i, weight=1)


def replace_keys_in_js(json_file, folder_path):
    with open(json_file, 'r', encoding='utf-8') as json_file:
        translation_dict = json.load(json_file)
    total_files = sum(1 for root, dirs, files in os.walk(folder_path) for filename in files if filename.endswith('.js'))

    progress = Tk()
    progress.title('替换进度')

    progress_title = Label(progress, text="替换进度")
    progress_title.grid(row=0, column=0, pady=20, padx=20)
    progress_lb = Label(progress, text="0/{}".format(total_files))
    progress_lb.grid(row=1, column=0, pady=20, padx=20)
    progress_bar = Progressbar(progress, length=300, mode='determinate', maximum=total_files)
    progress_bar.grid(row=1, column=1, pady=20, padx=20)

    progress.update_idletasks()
    x = (progress.winfo_screenwidth() // 2) - (progress.winfo_width() // 2) + 250
    y = (progress.winfo_screenheight() // 2) - (progress.winfo_height() // 2)
    progress.geometry('{}x{}+{}+{}'.format(700, 200, x, y))
    current_progress = 0
    # 处理替换
    for file_path in glob.glob(os.path.join(folder_path, '**/*.js'), recursive=True):
        with open(file_path, 'r', encoding='utf-8') as file:
            js_content = file.read()
        for key, value in translation_dict.items():
            js_content = js_content.replace(f'{key}', f'{value}')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(js_content)

        current_progress += 1
        progress_lb.config(text="{}/{}".format(current_progress, total_files))
        progress_lb.update()
        if current_progress < total_files:
            progress_bar.step(1)
            progress_bar.update()

    success_label = Label(progress, text="KubeJS翻译工具回填翻译成功！", font=("微软雅黑", 22, "bold"))
    success_label.grid(row=2, column=0, columnspan=2, padx=10)
    progress.update()
    time.sleep(2)
    progress.destroy()


def runFromGui():
    if len(kubejs_var.get()) == 0 and mode_entry.get() == '提取':
        dialogs.show_message('错误', '你需要选一个文件夹。')
    elif mode_entry.get() == '提取' and not replace2_var.get():
        # 遍历文件夹里的所有.js文件
        for file_path in glob.glob(os.path.join(kubejs_var.get(), '**/*.js'), recursive=True):
            with open(file_path, 'r', encoding='utf-8') as file:
                js_content = file.read()
            # 使用正则表达式匹配前缀并提取内容
            for prefix in prefixes:
                pattern = re.compile(rf'{prefix}\s*\([\'"]([^\'"]+)[\'"]\)')
                matches = pattern.findall(js_content)
                for match in matches:
                    # 生成随机键
                    random_key = f'kubejs.{os.path.basename(file_path)[:-3]}.{"".join(choices("abcdefghijklmnopqrstuvwxyz", k=5))}'
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
                             'KubeJS翻译工具提取翻译成功，'
                             '\njson已保存在当前程序所在的文件夹中\n注意，本工具提取不全，请人工检查未提取内容')
    elif mode_entry.get() == "提取" and replace2_var.get():
        total_files = sum(
            1 for root, dirs, files in os.walk(kubejs_var.get()) for filename in files if filename.endswith('.js'))

        progress = Tk()
        progress.title('替换进度')

        progress_title = Label(progress, text="替换进度")
        progress_title.grid(row=0, column=0, pady=20, padx=20)
        progress_lb = Label(progress, text="0/{}".format(total_files))
        progress_lb.grid(row=1, column=0, pady=20, padx=20)
        progress_bar = Progressbar(progress, length=300, mode='determinate', maximum=total_files)
        progress_bar.grid(row=1, column=1, pady=20, padx=20)

        progress.update_idletasks()
        x = (progress.winfo_screenwidth() // 2) - (progress.winfo_width() // 2) + 250
        y = (progress.winfo_screenheight() // 2) - (progress.winfo_height() // 2)
        progress.geometry('{}x{}+{}+{}'.format(700, 200, x, y))
        current_progress = 0
        # 遍历文件夹里的所有.js文件
        for file_path in glob.glob(os.path.join(kubejs_var.get(), '**/*.js'), recursive=True):
            with open(file_path, 'r', encoding='utf-8') as file:
                js_content = file.read()
            # 正则表达式匹配所有带单引号，双引号的内容
            pattern = re.compile(r"[\'\"]([^\'\"\[\]]+)[\'\"](?:\([^)]*\))?(?:\[[^]]*])?")
            matches = pattern.findall(js_content)
            for match in matches:
                # 生成随机键
                random_key = f'kubejs.{os.path.basename(file_path)[:-3]}.{"".join(choices("abcdefghijklmnopqrstuvwxyz", k=5))}'
                # 替换匹配的内容为随机键，包括方括号内的内容
                js_content = js_content.replace(f'(\'{match}\')', f'(\'{random_key}\')').replace(f'[{match}]',
                                                                                                 f'[{random_key}]')
                # 添加到翻译字典中
                translation_dict[random_key] = match

            current_progress += 1
            progress_lb.config(text="{}/{}".format(current_progress, total_files))
            progress_lb.update()
            if current_progress < total_files:
                progress_bar.step(1)
                progress_bar.update()
            # 写回原始文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(js_content)
        # 保存提取出的内容为en_us.json文件
        with open("en_us.json", 'w', encoding='utf-8') as json_file:
            json.dump(translation_dict, json_file, indent=2, ensure_ascii=False)

            success_label = Label(progress, text="提取成功！注意，当前使用了提取模式为暴力替换，请人工检查无效内容",
                                  font=("微软雅黑", 16, "bold"))
            success_label.grid(row=2, column=0, columnspan=2, padx=10)
            progress.update()
            time.sleep(3)
            progress.destroy()
    elif len(json_var.get()) == 0 and len(kubejs_var.get()) == 0 and mode_entry.get() == '回填':
        dialogs.show_message('错误', '你需要选一个json文件和一个文件夹。')
    elif len(json_var.get()) == 0 and mode_entry.get() == '回填':
        dialogs.show_message('错误', '你需要选一个json文件。')
    elif len(kubejs_var.get()) == 0 and mode_entry.get() == '回填':
        dialogs.show_message('错误', '你需要选一个文件夹。')
    elif mode_entry.get() == '回填':
        replace_keys_in_js(json_var.get(), kubejs_var.get())


def replace2():
    if replace2_var.get():
        replace_mode2 = dialogs.ask_yes_no('警告',
                                           '此模式将会把所有字符串替换为随机键，提取后语言文件内的行数将会激增，'
                                           '\n包括id等。也会给汉化人员造成不便。但是可以保证 100% 提取。'
                                           '\n\n如果不使用回填功能将无法启动游戏。确认开启吗？')
        if not replace_mode2:
            replace2_var.set(False)


root = Tk()
if sys.platform == "win32":
    try:
        # >= Windows 8.1
        ScaleFactor = ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except:
        # <= Windows 8.0
        ScaleFactor = ctypes.windll.user32.SetProcessDPIAware(0)


root.title("KubeJS翻译工具 1.2")
root.iconbitmap(bitmap="icon.ico")
kubejs_var, json_var = StringVar(), StringVar()
kubejs_entry = Entry(textvariable=kubejs_var)
json_entry = Entry(textvariable=json_var)
kubejs_lb = Label(text="选择处理 KubeJS 的文件夹", font=10)
json_lb = Label(text="选择 json 语言文件（仅回填模式）", font=10)
kubeJSButton = Button(text="选择", command=browseKubeJS)
jsonButton = Button(text="选择", command=browseJson)
mode_lb = Label(text="工作模式", font=10)
mode_list = ["提取", "回填"]
mode_entry = Combobox(state="readonly", values=mode_list)
mode_entry.bind("<<ComboboxSelected>>", on_mode_select)
sv_ttk.use_light_theme()
sv_ttk_theme = Checkbutton(text="暗色模式", style="Switch.TCheckbutton", command=sv_ttk.toggle_theme)
saveButton = Button(text="生成", style="Accent.TButton", command=runFromGui)
replace2_var = BooleanVar()
replaceButton = Checkbutton(root, text="暴力替换", variable=replace2_var, command=replace2)

gui()
root.update_idletasks()
x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2) + 250
y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
root.geometry('{}x{}+{}+{}'.format(740, 330, x, y))

if __name__ == "__main__":
    root.mainloop()
