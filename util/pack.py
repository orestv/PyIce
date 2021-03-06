import pickle
import StringIO

def pack(obj):
    buf = StringIO.StringIO()
    pickle.dump(obj, buf)
    buf.seek(0)
    result = buf.getvalue()
    buf.close()
    return result

def unpack(obj):
    if not obj:
        return None
    buf = StringIO.StringIO(obj)
    res = pickle.load(buf)
    buf.close()
    return res
