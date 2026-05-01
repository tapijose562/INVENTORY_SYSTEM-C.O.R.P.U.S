try:
    import importlib, sys, os
    print('cwd=', os.getcwd())
    print('sys.path[:5]=', sys.path[:5])
    print('listing cwd:', os.listdir('.'))
    try:
        m = importlib.import_module('app')
        print('Imported app package:', getattr(m, '__file__', repr(m)))
    except Exception as e:
        print('Importing app package failed:', e)
    importlib.import_module('app.main')
    print('Imported app.main OK')
except Exception as e:
    import traceback
    traceback.print_exc()
