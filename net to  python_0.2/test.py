import difflib

file1 = r"D:\Production_Python\Anpt_.net_to_python_service\net to  python_0.2\app.py"
file2 = r"D:\Production_Python\Anpt_.net_to_python_service\net_to_python\app.py"

with open(file1, "r") as f1, open(file2, "r") as f2:
   diff = difflib.unified_diff(f1.readlines(),
f2.readlines(), fromfile=file1, tofile=file2)

for line in diff:
   print(line)