#!/usr/bin/env python

from inspect import (getframeinfo, currentframe, getouterframes, getdoc, getsource)

class classSelfDoc(object):

    @property
    def frameName(self):
        frame = getframeinfo(currentframe().f_back)
        return str(frame.function)

    @property
    def frameDoc(self):
        frame = getframeinfo(currentframe().f_back)
        doc = eval('self.'+str(frame.function)+'.__doc__')
        return doc if doc else 'undocumented'

def frameName():
    return str(getframeinfo(currentframe().f_back).function)

def frameDoc():
    doc = eval(getframeinfo(currentframe().f_back).function).__doc__
    return doc if doc else 'undocumented'

def frameSource():
    return getsource(currentframe().f_back)

def SelfDoc(func):
    def documented():
        ret = func()
    func.doc = func.__doc__
    return documented

if __name__ == "__main__":

    class aClass(classSelfDoc):
        "class documentation"

        def __init__(self):
            "ctor documentation"
            print self.frameName, self.frameDoc

        def __call__(self):
            "ftor documentation"
            print self.frameName, self.frameDoc

        def undocumented(self):
            print self.frameName, self.frameDoc

    @SelfDoc
    def aDocumentedFunction():
        "function documentation"
        print frameName(), frameDoc()

    @SelfDoc
    def anUndocumentedFunction():
        print frameName(), frameDoc()
        print frameSource()

    anInstance = aClass()
    anInstance()
    anInstance.undocumented()

    aDocumentedFunction()
    anUndocumentedFunction()

    def foo():
        "foo OK"

    foo()
