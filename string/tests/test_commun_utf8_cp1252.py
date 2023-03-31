for i in range(256):
    try:
        cp1252 = bytes([i]).decode("cp1252")
        utf8 = bytes([i]).decode("utf-8")
        print(str(i) + "\t" + repr(cp1252))
    except:
        pass
