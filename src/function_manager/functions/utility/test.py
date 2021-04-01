filename = 'main.py'
with open(filename, 'r') as f:
    code = compile(f.read(), filename, mode='exec')
ctx = {}
exec(code, ctx)
eval('main(runtime)', {'runtime':1})