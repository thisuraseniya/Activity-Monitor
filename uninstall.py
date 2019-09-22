from winreg import *

print("Locating the Registry Keys")
aReg = ConnectRegistry(None, HKEY_CURRENT_USER)
aKey = OpenKey(aReg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 0, KEY_SET_VALUE)
try:
    DeleteValue(aKey, "Activity Tracker UCSC")
    print("Successfully deleted Activity Tracker from registry, you can now safely delete Activity Tracker")
except (FileNotFoundError, OSError, Exception):
    print("Activity Tracker already uninstalled, you can safely delete Activity Tracker")
CloseKey(aKey)
input("Press ENTER to exit")






