import ctypes
import win32api
import win32con
import win32gui
import win32ui
# 1.The error happened because the function needs  four arguments .
#  win32gui.MessageBox()

#2. We gave four arguments: window handle  message , title,and button type.
win32gui.MessageBox(0, "עילי פנסו","כרטיס זיהוי משתמש",win32con.MB_YESNO)

# 3.The |operator  lets us  combine two  constants together .
win32gui.MessageBox(
    0, "ישי ריבו ", "השמעת פלייליסט מוזיקלי",win32con.MB_YESNO  |win32con.MB_HELP
)


# 4.The function returns a number based on what was clicked: 6 for Yes and 7 for No.
result =win32gui.MessageBox(
    0, "ישי ריבו", "השמעת פלייליסט מוזיקלי", win32con.MB_YESNO | win32con.MB_HELP
)
if result ==win32con.IDYES:
  print("סיבת הסיבות")
elif result== win32con.IDNO:
  print("הפעולה בוטלה")

# 5. Running MessageBox  from win32api with all the parameters.
win32api.MessageBox(
    0, "טעינת נתוני מערכת הושלמה בהצלחה!", "התראת אבטחה win32api", 0
)

#6. It worked because this package has default values for some parameters.
win32api.MessageBox(0, "עילי פנסו", "כרטיס זיהוי משתמש", win32con.MB_YESNO)

#7.Here the first  parameter is the text. Putting 0 first will crash Python.
win32ui.MessageBox(
    "ברוכים הבאים לממשק המשתמש win32ui", "מערכת ניהול חלונות", win32con.MB_OK
)

# 8.The system DLL that has this  function is user32.dll.
user32 =ctypes.WinDLL("user32.dll")

# 9.It failed because the DLL only has MessageBoxA and MessageBoxW.
# user32.MessageBox()

#10.Calling MessageBoxW opens the window  successfully.
user32.MessageBoxW(
    0, "גישה ישירה ל- user32.dll בוצעה בהצלחה!",  "התראה מתקדמת ctypes", 0
)
