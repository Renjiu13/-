import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import threading
import os
import sys

class ImageSizeCheckerApp:
    def __init__(self, master):
        self.master = master
        master.title("图片尺寸检查工具")
        master.geometry("600x600")
        
        # 设置窗口图标
        self.set_window_icon(master)
        
        # 样式
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("微软雅黑", 10))
        self.style.configure("TButton", font=("微软雅黑", 10))
        
        # 文件夹路径
        self.path_label = ttk.Label(master, text="选择检查文件夹:")
        self.path_label.pack(pady=(10,0))
        
        self.path_frame = ttk.Frame(master)
        self.path_frame.pack(pady=(5,10), padx=20, fill='x')
        
        self.path_entry = ttk.Entry(self.path_frame, width=40)
        self.path_entry.pack(side='left', expand=True, fill='x', padx=(0,10))
        
        self.browse_button = ttk.Button(self.path_frame, text="浏览", command=self.browse_folder)
        self.browse_button.pack(side='right')
        
        # 尺寸设置框架
        self.size_frame = ttk.Frame(master)
        self.size_frame.pack(pady=(5,10), padx=20, fill='x')
        
        ttk.Label(self.size_frame, text="目标尺寸:").pack(side='left')
        
        self.width_entry = ttk.Entry(self.size_frame, width=8)
        self.width_entry.insert(0, "1200")
        self.width_entry.pack(side='left', padx=5)
        
        ttk.Label(self.size_frame, text="x").pack(side='left')
        
        self.height_entry = ttk.Entry(self.size_frame, width=8)
        self.height_entry.insert(0, "1200")
        self.height_entry.pack(side='left', padx=5)
        
        # 特定文件夹选项
        self.specific_frame = ttk.Frame(master)
        self.specific_frame.pack(pady=(5,10), padx=20, fill='x')
        
        self.specific_var = tk.BooleanVar(value=False)
        self.specific_check = ttk.Checkbutton(
            self.specific_frame, 
            text="只检查特定文件夹", 
            variable=self.specific_var,
            command=self.toggle_specific_folder
        )
        self.specific_check.pack(side='left')
        
        self.specific_entry = ttk.Entry(self.specific_frame, width=20, state='disabled')
        self.specific_entry.pack(side='left', padx=(10,0))
        
        # 忽略文件夹
        self.ignore_label = ttk.Label(master, text="忽略的文件夹:")
        self.ignore_label.pack(pady=(10,0))
        
        self.ignore_frame = ttk.Frame(master)
        self.ignore_frame.pack(pady=(5,10), padx=20, fill='x')
        
        self.ignore_entries = []
        default_ignores = ["03-辅料", "04-细节图", "01-商品轮播展示图"]
        for ignore in default_ignores:
            entry = ttk.Entry(self.ignore_frame, width=15)
            entry.insert(0, ignore)
            entry.pack(side='left', padx=5)
            self.ignore_entries.append(entry)
        
        # 添加忽略文件夹按钮
        self.add_ignore_button = ttk.Button(
            self.ignore_frame, 
            text="+", 
            width=3, 
            command=self.add_ignore_entry
        )
        self.add_ignore_button.pack(side='left', padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(
            master, 
            orient='horizontal', 
            length=300, 
            mode='indeterminate'
        )
        self.progress.pack(pady=(10,0))
        
        # 开始检查按钮
        self.check_button = ttk.Button(
            master, 
            text="开始检查", 
            command=self.start_check
        )
        self.check_button.pack(pady=(10,0))
        
        # 结果显示区域
        self.result_frame = ttk.Frame(master)
        self.result_frame.pack(pady=(10,0), expand=True, fill='both')
        
        # 创建文本框
        self.result_text = tk.Text(
            self.result_frame, 
            height=15, 
            width=80, 
            wrap='none',  # 不自动换行
            font=('Consolas', 10)  # 使用等宽字体方便复制
        )
        self.result_text.pack(side='left', expand=True, fill='both')
        
        # 垂直滚动条
        y_scrollbar = ttk.Scrollbar(
            self.result_frame, 
            orient='vertical', 
            command=self.result_text.yview
        )
        y_scrollbar.pack(side='right', fill='y')
        
        # 水平滚动条
        x_scrollbar = ttk.Scrollbar(
            self.result_frame, 
            orient='horizontal', 
            command=self.result_text.xview
        )
        x_scrollbar.pack(side='bottom', fill='x')
        
        # 配置文本框滚动
        self.result_text.configure(
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
    
    def set_window_icon(self, master):
        """设置窗口图标"""
        try:
            # 如果是打包后的exe
            if getattr(sys, 'frozen', False):
                icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
            # 如果是普通Python脚本
            else:
                icon_path = 'icon.ico'
            
            master.iconbitmap(icon_path)
        except Exception:
            pass  # 如果图标加载失败，不影响程序运行
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_path)
    
    def toggle_specific_folder(self):
        if self.specific_var.get():
            self.specific_entry.config(state='normal')
        else:
            self.specific_entry.config(state='disabled')
    
    def add_ignore_entry(self):
        entry = ttk.Entry(self.ignore_frame, width=15)
        entry.pack(side='left', padx=5)
        self.ignore_entries.append(entry)
    
    def start_check(self):
        # 清空之前的结果
        self.result_text.delete(1.0, tk.END)
        
        # 获取输入参数
        input_path = self.path_entry.get().strip()
        if not input_path:
            messagebox.showerror("错误", "请选择文件夹")
            return
        
        # 获取目标尺寸
        try:
            target_width = int(self.width_entry.get().strip())
            target_height = int(self.height_entry.get().strip())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的尺寸数值")
            return
        
        # 获取忽略的文件夹
        ignore_folders = [
            entry.get().strip() 
            for entry in self.ignore_entries 
            if entry.get().strip()
        ]
        
        # 获取特定文件夹
        specific_folder = None
        if self.specific_var.get():
            specific_folder = self.specific_entry.get().strip()
        
        # 启动进度条
        self.progress.start()
        self.check_button.config(state='disabled')
        
        # 在单独线程中运行检查，避免UI冻结
        def run_check():
            try:
                results = self.check_image_sizes(
                    input_path, 
                    target_width,
                    target_height,
                    specific_folder, 
                    ignore_folders
                )
                
                # 回到主线程更新UI
                self.master.after(0, self.update_results, results)
            except Exception as e:
                self.master.after(0, self.show_error, str(e))
        
        threading.Thread(target=run_check, daemon=True).start()
    
    def check_image_sizes(self, input_path, target_width, target_height, specific_folder=None, ignore_folders=None):
        """
        检查图片尺寸的核心逻辑
        """
        results = []
        
        for root, dirs, files in os.walk(input_path):
            current_folder = os.path.basename(root)
            
            # 检查是否符合文件夹条件
            if specific_folder and current_folder != specific_folder:
                continue
            
            if current_folder in ignore_folders:
                continue
            
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    file_path = os.path.join(root, file)
                    try:
                        with Image.open(file_path) as img:
                            width, height = img.size
                            if width != target_width or height != target_height:
                                results.append(f"文件: {file_path} - 实际尺寸: {width}x{height}")
                    except Exception as e:
                        results.append(f"文件: {file_path} - 错误: {str(e)}")
        
        return results
    
    def update_results(self, results):
        # 停止进度条
        self.progress.stop()
        self.check_button.config(state='normal')
        
        # 清空之前的结果
        self.result_text.delete(1.0, tk.END)
        
        # 显示结果
        if results:
            # 添加标题和统计信息
            self.result_text.tag_configure('title', foreground='blue', font=('微软雅黑', 10, 'bold'))
            self.result_text.insert(tk.END, f"发现 {len(results)} 个不符合尺寸的图片。\n", 'title')
            self.result_text.insert(tk.END, "-" * 50 + "\n", 'title')
            
            # 逐行添加结果，每行都易于复制
            for result in results:
                self.result_text.insert(tk.END, result + "\n")
        else:
            self.result_text.insert(tk.END, "所有图片尺寸均符合要求。\n")
        
        # 滚动到底部
        self.result_text.see(tk.END)
    
    def show_error(self, error_msg):
        # 停止进度条
        self.progress.stop()
        self.check_button.config(state='normal')
        
        # 显示错误
        messagebox.showerror("错误", error_msg)

def main():
    root = tk.Tk()
    app = ImageSizeCheckerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
