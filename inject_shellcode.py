from pymem import Pymem

p = "wowclassic.exe"

pm = Pymem(p)
asd = pm.inject_python_interpreter()
f = open("pythonHookMainThread.py", "r", encoding="utf-8")
shellcode = f.read()
pm.inject_python_shellcode(shellcode)

