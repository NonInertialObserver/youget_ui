import os.path
from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askdirectory


class PathChooseFrame(Frame):
    def __init__(self, master = None, *, border = 0, borderwidth = 0, class_ = "", cursor = "", height = 0, name = '', padding = 0, 
                 relief = FLAT, style = "", takefocus = "", width = 0, prompt:str= '请选择文件', textvariable=None):
        super().__init__(master, border=border, borderwidth=borderwidth, class_=class_, cursor=cursor, height=height, name=name, padding=padding, 
                         relief=relief, style=style, takefocus=takefocus, width=width)
        
        if not textvariable:
            textvariable=StringVar()
        self.textvariable=textvariable
        self._path_l = Label(self, text=prompt)
        self._path_e = Entry(self, background='white',textvariable=textvariable)  
        self._path_b = Button(self, text='...', command=self._setpath)

    def _setpath(self):
        path = askdirectory()
        if path:
            self.textvariable.set(path)
    
    def pack(self, **kwargs):
        self._path_l.pack(side=LEFT,)
        self._path_e.pack(side=LEFT, fill=X, expand=True,)
        self._path_b.pack(side=RIGHT,)
        self._path_e.config(state='readonly')
        super().pack(**kwargs)
    
    def grid(self, **kwargs):
        self._path_l.grid(row=0, column=0, sticky='ew', **kwargs)
        self._path_e.grid(row=0, column=1, sticky='ew', **kwargs)
        self._path_b.grid(row=0, column=2, **kwargs)
        super().grid(**kwargs)
    
    def place(self, **kwargs):
        self._path_l.place(**kwargs)
        self._path_e.place(**kwargs)
        self._path_b.place(**kwargs)
        super().place(**kwargs)

    def get(self):
        return self.textvariable.get()
    
    def checked_path(self):
        path = self.get()
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path '{path}' does not exist.")
        
        self.textvariable.set(path)
        return path
    
    def set(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path '{path}' does not exist.")
        self.textvariable.set(path)
    
if __name__ == '__main__':
    root = Tk()
    root.geometry('400x100')
    frame = PathChooseFrame(root, prompt='请选择目录:')
    frame.pack()
    
    def show_path():
        print(frame.get())
    
    Button(root, text='Show Path', command=show_path).pack(pady=10)
    
    root.mainloop()