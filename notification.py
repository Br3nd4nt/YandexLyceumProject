import os
import platform


class Notification:
    def __init__(self):
        self.OS = platform.system()
        

    def notify(self, title, text):
        if self.OS == 'Darwin':
            os.system(f"""
                osascript -e 'display notification "{title}" with title "{text}"'
                """)
        elif self.OS == "win32" or self.OS == "win64":
            try:
                from win10toast import ToastNotifier
                toast = ToastNotifier()
                toast.showToast(title, text, duration=20)
            except Exception as e:
                print(e)
