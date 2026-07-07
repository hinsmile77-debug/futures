import pickle, os, sys
model_dir  = r'C:\Users\82108\PycharmProjects\futures\model\horizons'
scaler_dir = r'C:\Users\82108\PycharmProjects\futures\model\scaler'
print("Python:", sys.version.split()[0], "32-bit" if sys.maxsize <= 2**32 else "64-bit")
errors = []
for hz in ['1m','3m','5m','10m','15m','30m']:
    try:
        with open(os.path.join(model_dir,  'gbm_'+hz+'.pkl'),          'rb') as f: m  = pickle.load(f)
        with open(os.path.join(scaler_dir, 'scaler_'+hz+'.pkl'),       'rb') as f: s  = pickle.load(f)
        with open(os.path.join(model_dir,  'feature_names_'+hz+'.pkl'),'rb') as f: fn = pickle.load(f)
        print(hz+": OK | "+type(m).__name__+" | "+type(s).__name__+" | features="+str(len(fn)))
    except Exception as e:
        errors.append(hz)
        print(hz+": FAIL | "+str(e))
print("---")
print("결과:", "전체 성공" if not errors else str(len(errors))+"개 실패: "+str(errors))
sys.exit(0 if not errors else 1)
