import sys
pythontex_module = sys.modules['__main__']
STReq = getattr(pythontex_module, 'STReq', None)
if STReq is not None:
    steamtables = STReq.to_latex()
    if len(steamtables) > 0:
        print(steamtables)