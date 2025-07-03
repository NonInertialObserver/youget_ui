
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import subprocess
import os
import sys
import locale

# import you_get.version

import settings
        
import widgets

class YouGetUI:
    def __init__(self, root:tk.Tk):
        self.root = root
        root.title("You-Get GUI Downloader")
        root.iconbitmap("./icon.ico")
        root.geometry("700x500")
        root.resizable(True, True)
        
        # 检测系统编码
        self.system_encoding = locale.getpreferredencoding()
        
        # 设置主题样式
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'), foreground='#333')
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        header = ttk.Label(self.main_frame, text="You-Get 视频下载器", style='Header.TLabel')
        header.pack(pady=(0, 2))
        
        # URL输入部分
        url_frame = ttk.Frame(self.main_frame)
        url_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(url_frame, text="视频URL:").pack(side=tk.LEFT, padx=(0, 1))
        self.url_entry = ttk.Entry(url_frame, width=60)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.url_entry.focus()
        
        # 设置默认参数
        self.path_var = widgets.StringVar(value=os.path.expanduser("~/Downloads"))
        self.proxy_type_var = widgets.StringVar(value="HTTP")
        self.proxy_var = widgets.StringVar()

        
        # 清晰度选择
        quality_frame = ttk.Frame(self.root)
        quality_frame.pack(fill=tk.X, pady=1)
        
        ttk.Label(quality_frame, text="视频清晰度:").pack(side=tk.LEFT, padx=(0, 10))
        self.quality_var = tk.StringVar()        
        quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality_var, width=15)
        quality_combo['values'] = ('自动选择', '超清4K', '高清1080p', '标清480p')
        quality_combo.current(0)
        quality_combo.pack(side=tk.LEFT)

        # 设置按钮
        settings_btn = ttk.Button(self.main_frame, text="设置...", command=self.open_settings)
        settings_btn.pack(anchor='ne', padx=2, pady=2)
        
        # 控制按钮
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=1)
        self.download_btn = ttk.Button(btn_frame, text="开始下载", command=self.start_download)
        self.download_btn.pack(side=tk.LEFT, padx=5)
        self.cancel_btn = ttk.Button(btn_frame, text="取消", command=self.cancel_download, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # 日志输出
        log_frame = ttk.LabelFrame(self.main_frame, text="下载日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(2, 0), side=tk.BOTTOM)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        
        # 下载控制变量
        self.download_process = None
        self.is_downloading = False

    def open_settings(self):
        def on_save(path, proxy_type, proxy):
            self.path_var.set(path)
            self.proxy_type_var.set(proxy_type)
            self.proxy_var.set(proxy)
        win = settings.SettingsToplevel(self.root)
        win.save_settings(on_save)
        win.grab_set()
        
    
    def browse_directory(self):
        """选择下载目录（已集成在PathChooseFrame中，无需单独按钮）"""
        pass
    
    def start_download(self):
        """开始下载视频"""
        if self.is_downloading:
            return
            
        url = self.url_entry.get().strip()
        if not url:
            self.log_message("错误：请输入有效的视频URL")
            return
        
        download_path = self.path_var.get()
        if not os.path.isdir(download_path):
            try:
                os.makedirs(download_path, exist_ok=True)
            except Exception as e:
                self.log_message(f"创建目录失败: {str(e)}")
                return
        
        # 构建you-get命令
        quality_map = {'自动选择': '', '超清': '--format=4K', '高清': '--format=1080p', '标清': '--format=480p'}
        quality_flag = quality_map[self.quality_var.get()]
        
        cmd = ['you-get', '-o', download_path]
        if quality_flag:
            cmd.append(quality_flag)
            
        # 添加代理设置
        proxy = self.proxy_var.get().strip()
        proxy_type = self.proxy_type_var.get()
        if proxy:
            if proxy_type == "SOCKS":
                cmd.extend(['--socks-proxy', proxy])
            else:
                cmd.extend(['--http-proxy', proxy])
        cmd.append(url)
        
        self.log_message(f"开始下载: {url}")
        self.log_message(f"命令: {' '.join(cmd)}")
        
        # 更新UI状态
        self.is_downloading = True
        self.download_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.status_var.set("下载中...")
        
        # 在新线程中运行下载
        download_thread = threading.Thread(target=self.run_download, args=(cmd,))
        download_thread.daemon = True
        download_thread.start()
    
    def run_download(self, cmd):
        """执行下载命令（修复编码问题）"""
        try:
            # 修复编码问题：使用UTF-8编码
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            self.download_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                env=env
            )
            
            # 实时读取输出（处理编码问题）
            while True:
                line = self.download_process.stdout.readline()
                if not line:
                    break
                    
                try:
                    # 尝试UTF-8解码
                    decoded_line = line.decode('utf-8').strip()
                except UnicodeDecodeError:
                    try:
                        # 尝试系统默认编码
                        decoded_line = line.decode(self.system_encoding, errors='replace').strip()
                    except:
                        # 最后尝试忽略错误
                        decoded_line = line.decode(errors='ignore').strip()
                
                self.log_message(decoded_line)
            
            return_code = self.download_process.wait()
            
            if return_code == 0:
                self.log_message("下载完成！")
                self.status_var.set("下载完成")
            else:
                self.log_message(f"下载失败，错误码: {return_code}")
                self.status_var.set("下载失败")
                
        except Exception as e:
            error_msg = str(e)
            try:
                # 尝试UTF-8编码错误信息
                error_msg = error_msg.encode('utf-8').decode('utf-8')
            except:
                pass
            self.log_message(f"发生错误: {error_msg}")
            self.status_var.set("发生错误")
        finally:
            self.is_downloading = False
            self.root.after(0, self.reset_ui)
    
    def cancel_download(self):
        """取消下载"""
        if self.is_downloading and self.download_process:
            self.log_message("正在取消下载...")
            try:
                # 尝试终止进程
                self.download_process.terminate()
                # 等待进程结束
                self.download_process.wait(timeout=3)
            except:
                pass
            finally:
                self.is_downloading = False
                self.status_var.set("已取消")
    
    def reset_ui(self):
        """重置UI状态"""
        self.download_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
    
    def log_message(self, message):
        """向日志区域添加消息（处理编码问题）"""
        safe_message = self.sanitize_text(message)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, safe_message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
    
    def sanitize_text(self, text):
        """处理文本中的非法字符"""
        try:
            # 尝试UTF-8编码
            return text.encode('utf-8', 'replace').decode('utf-8')
        except:
            # 如果失败，使用错误替换
            return text.encode(errors='replace').decode(errors='replace')

def main():
    # 检查you-get是否安装
    try:
        subprocess.run(['you-get', '--version'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL,
                      check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        result = messagebox.askyesno(
            "依赖缺失",
            "未找到you-get，是否要自动安装？\n\n安装方法: pip install you-get"
        )
        if result:
            try:
                # 尝试安装you-get
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'you-get'], check=True)
                messagebox.showinfo("安装成功", "you-get 已成功安装！")
            except Exception as e:
                messagebox.showerror("安装失败", f"安装you-get失败:\n{str(e)}")
                sys.exit(1)
        else:
            sys.exit(1)
    
    root = tk.Tk()
    app = YouGetUI(root)
    root.mainloop()

def yougettest():
    import you_get
    print(you_get.version)
    # you_get.main()

debug=True
if __name__ == "__main__":
    print('start test...')
    if debug :
        yougettest()
        
    main()
