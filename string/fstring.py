# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 15:50:03 2021

@author: Baptiste
"""
from SmartFramework.serialize import serializejson


class fstring(str):
    def __new__(cls, content, **dictionnaire):
        self = str.__new__(cls, content.format(**dictionnaire))
        self._content = content
        return self

    # def __reduce__(self):
    #    return fstring,self._content
    # def __new__(cls,string,**kargs):
    #    return self
    # return string.format(**kargs)
    #    string = str(string)
    ##    self._dictionaire = dictionaire
    #    return ()
    # def setDictionnaire(self,dictionnaire):
    #    self._dictionaire = dictionnaire
    # def __str__(self):
    #    return self.format(self._dictionaire)


a = fstring("{mot} toi", mot=1)
b = str.format("{mot} toi", mot=1)


print(a)
print(b)
print(serializejson.dumps(a))
print(serializejson.dumps(b))
