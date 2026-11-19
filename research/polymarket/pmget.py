import json,urllib.request,time
def g(u):
    for i in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}),timeout=30))
        except Exception as e: err=e; time.sleep(2)
    raise err
