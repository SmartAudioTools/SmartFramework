try:
    import sys
    import os
    from SmartFramework.serialize import serializejson
    from SmartFramework.files import name, cleanDropNames

    cleanDropNames(sys.argv)

    for jsonPath in sys.argv[1:]:
        print(name(jsonPath) + ": ", end=" ")
        json = serializejson.load(
            jsonPath, unauthorized_classes_as_dict=True, dotdict=True
        )  # , numpy_array_from_list = True
        serializejson.dump(json, jsonPath, numpy_array_readable_max_size=12)

    print("\n")
    os.system("pause")

except:
    import traceback

    traceback.print_exc()
    print("\n")
    os.system("pause")
