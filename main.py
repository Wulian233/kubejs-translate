import ctypes
import glob
import json
import os
import re
import sys
import time
from random import choices
from tkinter import filedialog, StringVar, BooleanVar, Tk, DISABLED, END, NORMAL, WORD, Text
from tkinter.ttk import *
import sv_ttk
import dialogs
import threading

# 匹配的前缀
prefixes = [
    "displayName", "tooltip", "tell", "yellow", "Text.of",
    "white", "green", "gray", "gold", "darkPurple",
    "blue", "darkGreen", "aqua", "red", "string", "lightPurple"
]

# 定义存储键值对的字典
translation_dict = {}

def browseJson():
    json_var.set(
        filedialog.askopenfilename(filetypes=(('选择 json 语言文件', "*.json"),),
                                   initialdir=os.path.abspath(os.path.dirname(__file__))))
def browseEnglishJson():
    translate_var.set(
        filedialog.askopenfilename(filetypes=(('选择 json 英文语言文件', "*.json"),),
                                   initialdir=os.path.abspath(os.path.dirname(__file__))))

def browseKubeJS():
    kubejs_var.set(
        filedialog.askdirectory(title='选择处理 KubeJS 的文件夹',
                                initialdir=os.path.abspath(os.path.dirname(__file__))))

def start_ai_translate():
    threading.Thread(target=ai_translate).start()

def ai_translate():
    if translate_var.get() == "":
        dialogs.show_message("错误", "请先选择json文件")
    else:
        sys.stdout = output_text
        print('正在加载模型，请稍等，预计8秒左右\n')
        root.update_idletasks()
        from transformers import MarianMTModel, MarianTokenizer

        start_time = time.time()
        tokenizer = MarianTokenizer.from_pretrained('model')
        model = MarianMTModel.from_pretrained('model')

        print('加载模型完成，正在加载英文语言文件，请稍等')
        root.update_idletasks()
        with open(translate_var.get(), 'r', encoding='utf-8') as f:
            data = json.load(f)
        print('加载完成，正在AI汉化中，请稍等（耗时与CPU性能有关）')
        root.update_idletasks()
        count = 0
        for key in data.keys():
            text = data[key]
            input_ids = tokenizer.encode(text, return_tensors='pt')
            outputs = model.generate(input_ids)
            translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            translated_text = translated_text.replace(',', '，').replace('!', '！').replace('?', '？').replace(': ', '：').replace('...', '…')
            data[key] = translated_text
            count += 1
            if count % 10 == 0:
                # 每翻译10条文本就保存一次
                with open('zh_cn.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f'已汉化完成{count}条翻译，并自动保存zh_cn.json')
                root.update_idletasks()  # Update the GUI

        end_time = time.time()
        total_time = end_time - start_time

        with open('zh_cn.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.close()

        print(f'AI一键汉化完成！共耗时{total_time}秒\n汉化文件zh_cn.json已保存至当前目录下')
        root.update_idletasks()
        dialogs.show_message('KubeJS翻译工具', f'AI一键汉化完成！共耗时{total_time}秒\n汉化文件zh_cn.json已保存至当前目录下')

def gui():
    r = 1
    json_lb.grid(row=r, column=0, pady=5, padx=20, sticky='nsew')
    json_entry.grid(row=r, column=1, pady=5, sticky='nsew')
    json_button.grid(row=r, column=2, pady=5, padx=30, sticky='nsew')
    r += 1
    kubejs_lb.grid(row=r, column=0, pady=5, padx=20, sticky='nsew')
    kubejs_entry.grid(row=r, column=1, pady=5, sticky='nsew')
    kubejs_button.grid(row=r, column=2, pady=5, padx=30, sticky='nsew')
    r += 2
    mode_lb.grid(row=r, column=0, pady=5, padx=20, sticky='nsew')
    mode_entry.current(0)
    mode_entry.grid(row=r, column=1, pady=5, padx=30, sticky='nsew')
    sv_ttk_theme.grid(row=r, column=2, pady=5, padx=30, sticky='nsew')
    r += 1
    replace_button.grid(row=r, column=1, pady=5, padx=30, sticky='nsew')
    save_button.grid(row=r, column=2, pady=5, padx=30, sticky='nsew')

    # 让列和行自适应
    for i in range(3):  # 列数
        tab1.columnconfigure(i, weight=1)
        tab2.columnconfigure(i, weight=1)

    for i in range(r + 1):  # 行数
        tab1.rowconfigure(i, weight=1)
        tab2.rowconfigure(i, weight=1)

    r = 1
    translate_lb.grid(row=r, column=0, pady=5, padx=20, sticky='nsew')
    translate_entry.grid(row=r, column=1, pady=5, sticky='nsew')
    translate_button.grid(row=r, column=2, pady=5, padx=30, sticky='nsew')
    r += 1
    translate_title.grid(row=r, column=0, pady=5, padx=20, sticky='nsew')
    output_text.grid(row=r, column=1, pady=5, padx=20, sticky='nsew')
    scrollbar.grid(row=r, column=2, padx=20, sticky="ns")
    r += 1
    save_translate_button.grid(row=r, column=2, pady=5, padx=20, sticky='nsew')

    notebook.grid(row=0, column=0, sticky='nsew')

def create_progress_bar(title, total_files):
    progress = Tk()
    progress.title(title)

    progress_title = Label(progress, text=title)
    progress_title.grid(row=0, column=0, pady=20, padx=20)
    progress_lb = Label(progress, text="0/{}".format(total_files))
    progress_lb.grid(row=1, column=0, pady=20, padx=20)
    progress_bar = Progressbar(progress, length=300, mode='determinate', maximum=total_files)
    progress_bar.grid(row=1, column=1, pady=20, padx=20)

    progress.update_idletasks()
    x = (progress.winfo_screenwidth() // 2) - (progress.winfo_width() // 2) + 250
    y = (progress.winfo_screenheight() // 2) - (progress.winfo_height() // 2)
    progress.geometry('{}x{}+{}+{}'.format(700, 200, x, y))

    return progress, progress_lb, progress_bar

def update_progress(progress_lb, progress_bar, current_progress, total_files):
    progress_lb.config(text="{}/{}".format(current_progress, total_files))
    progress_lb.update()
    if current_progress < total_files:
        progress_bar.step(1)
        progress_bar.update()

def replace_keys_in_js(json_file, folder_path):
    with open(json_file, 'r', encoding='utf-8') as json_file:
        translation_dict = json.load(json_file)

    total_files = sum(
        1 for root, dirs, files in os.walk(folder_path) for filename in files if filename.endswith('.js'))
    progress, progress_lb, progress_bar = create_progress_bar('替换进度', total_files)

    current_progress = 0
    for file_path in glob.glob(os.path.join(folder_path, '**/*.js'), recursive=True):
        with open(file_path, 'r', encoding='utf-8') as file:
            js_content = file.read()
        for key, value in translation_dict.items():
            js_content = js_content.replace(f'{key}', f'{value}')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(js_content)

        current_progress += 1
        update_progress(progress_lb, progress_bar, current_progress, total_files)

    success_label = Label(progress, text="KubeJS翻译工具回填翻译成功！", font=("微软雅黑", 22, "bold"))
    success_label.grid(row=2, column=0, columnspan=2, padx=10)
    progress.update()
    time.sleep(2)
    progress.destroy()


def runFromGui():
    if len(kubejs_var.get()) == 0 and mode_entry.get() == '提取':
        dialogs.show_message('错误', '请先选择文件夹。')
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
        progress, progress_lb, progress_bar = create_progress_bar('替换进度', total_files)

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
            update_progress(progress_lb, progress_bar, current_progress, total_files)
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

class ReadOnlyText(Text):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(state=DISABLED)

    def write(self, text):
        self.config(state=NORMAL)
        self.insert(END, text)
        self.see(END)
        self.config(state=DISABLED)

    def flush(self):
        pass

root = Tk()
if sys.platform == "win32":
    try:
        # >= Windows 8.1
        ScaleFactor = ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except OSError:
        # <= Windows 8.0
        ScaleFactor = ctypes.windll.user32.SetProcessDPIAware(0)

root.title("KubeJS翻译工具 1.3")
# root.iconbitmap(bitmap="icon.ico")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

notebook = Notebook(root)
tab1, tab2 = Frame(notebook), Frame(notebook)
notebook.add(tab1, text="工具")
notebook.add(tab2, text="大模型 AI 汉化")
kubejs_var, json_var, translate_var = StringVar(), StringVar(), StringVar()
kubejs_entry = Entry(tab1, textvariable=kubejs_var)
json_entry = Entry(tab1, textvariable=json_var)
translate_entry = Entry(tab2, textvariable=translate_var)

kubejs_lb = Label(tab1, text="选择处理 KubeJS 的文件夹", font=10)
json_lb = Label(tab1, text="选择 json 语言文件（仅回填模式）", font=10)
kubejs_button = Button(tab1, text="选择", command=browseKubeJS)
json_button = Button(tab1, text="选择", command=browseJson)
mode_lb = Label(tab1, text="工作模式", font=10)
mode_list = ["提取", "回填"]
mode_entry = Combobox(tab1, state="readonly", values=mode_list)
mode_entry.bind("<<ComboboxSelected>>")
sv_ttk.use_light_theme()
sv_ttk_theme = Checkbutton(tab1, text="暗色模式", style="Switch.TCheckbutton", command=sv_ttk.toggle_theme)
save_button = Button(tab1, text="生成", style="Accent.TButton", command=runFromGui)
replace2_var = BooleanVar()
replace_button = Checkbutton(tab1, text="暴力替换", variable=replace2_var, command=replace2)

translate_title = Label(tab2, text="使用本地AI汉化很慢！\nCPU占用约为50%左右", font=10)
translate_lb = Label(tab2, text="选择英文语言文件", font=10)
translate_button = Button(tab2, text="选择", command=browseEnglishJson)
save_translate_button = Button(tab2, text="一键汉化", style="Accent.TButton", command=start_ai_translate)
output_text = ReadOnlyText(tab2, wrap=WORD, width=40, height=10)
scrollbar = Scrollbar(tab2, command=output_text.yview)
output_text.config(yscrollcommand=scrollbar.set)

gui()
root.update_idletasks()
x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2) + 300
y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2) + 60
root.geometry('{}x{}+{}+{}'.format(770, 360, x, y))

if __name__ == "__main__":
    root.mainloop()
