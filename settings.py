from tkinter import *
from tkinter.ttk import *

import widgets

class SettingsToplevel(Toplevel):
    "the sub-window of settings "
    def __init__(self, master=None):
        super().__init__(master)
        self.title("设置")
        self.geometry("400x250")
        self.resizable(False, False)
        self.save_settings_func=self.default_save_settings

        # 路径选择
        self.download_path_var = widgets.StringVar()
        self.path_frame = widgets.PathChooseFrame(self, prompt="下载保存路径:", textvariable=self.download_path_var)
        self.path_frame.pack(fill='x', padx=20, pady=15)

        # 代理类型选择和代理地址输入
        proxy_type_frame = Frame(self)
        proxy_type_frame.pack(fill='x', padx=20, pady=5)
        Label(proxy_type_frame, text="代理类型:").pack(side=LEFT)
        self.proxy_type_var = widgets.StringVar(value="HTTP")
        http_rb = Radiobutton(proxy_type_frame, text="HTTP代理", variable=self.proxy_type_var, value="HTTP")
        http_rb.pack(side=LEFT, padx=5)
        socks_rb = Radiobutton(proxy_type_frame, text="SOCKS代理", variable=self.proxy_type_var, value="SOCKS")
        socks_rb.pack(side=LEFT, padx=5)

        self.proxy_var = widgets.StringVar()
        self.proxy_entry = widgets.PromptedEntry(self, prompt="代理地址:", textvariable=self.proxy_var)
        self.proxy_entry.pack(fill='x', padx=20, pady=5)

        # 按钮区
        btn_frame = Frame(self)
        btn_frame.pack(fill='x', pady=20)
        save_btn = Button(btn_frame, text="保存", command=self._save_settings)
        save_btn.pack(side=LEFT, padx=30)
        cancel_btn = Button(btn_frame, text="取消", command=self.destroy)
        cancel_btn.pack(side=RIGHT, padx=30)

    def default_save_settings(self,path,proxy_type,proxy):
        # 这里可以扩展为保存到配置文件或主窗口通信
        # 简单弹窗演示
        from tkinter import messagebox
        messagebox.showinfo("设置已保存", f"保存路径: {path}\n代理类型: {proxy_type}\n代理: {proxy}")
        self.destroy()

    def _save_settings(self):
        path = self.download_path_var.get()
        proxy_type = self.proxy_type_var.get()
        proxy = self.proxy_var.get()
        self.save_settings_func(path=path,proxy_type=proxy_type,proxy=proxy)


    #@
    def save_settings(self,func):
        self.save_settings_func = func
        # 这里可以扩展为保存到配置文件或主窗口通信
        return func

if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # 隐藏主窗口
    def on_save_settings(path, proxy_type, proxy):
        print(f"保存路径: {path}, 代理类型: {proxy_type}, 代理: {proxy}")
    # 创建设置窗口实例
    # 并传入保存设置的回调函数
    # 这里可以扩展为保存到配置文件或主窗口通信
    # 例如：settings_window.save_settings(on_save_settings)

    settings_window = SettingsToplevel(root)
    settings_window.save_settings(on_save_settings)
    settings_window.mainloop()
    root.destroy()  # 确保退出时销毁主窗口