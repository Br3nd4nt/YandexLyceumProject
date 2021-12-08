import os
import platform


class Notification:
    def __init__(self):
        self.OS = platform.system()
        

    def notify(self, title, text):
        if self.OS == 'Darwin':
            pass # implement later
        elif self.OS == "win32" or self.OS == "win64" or self.OS == 'Windows':
            try:
                import win10toast
                toast = win10toast.ToastNotifier()
                toast.show_toast(title, text, duration=5, icon_path='logo.ico')
            except Exception as e:
                print(e)




if __name__ == "__main__":
    n = Notification()
    print(platform.system())
    n.notify('1', '1')