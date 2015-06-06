#!/usr/bin/python3

from   decorator import decorator
from   inspect   import getfullargspec
import pickle

MAX_ARG_STRING  = 20
MAX_DATA_STRING = 80

# Storing variables
def storeAsString(self, varName):
  return ("", varName + "=" + repr(self))

def storeAsVar(self, varName):
  return (varName + " = " + repr(self), varName)

def writeTextFile(self, filename):
    with open(filename, "w") as outf:
        outf.write(repr(self))

def storeAsFile(self, varName, extension="in", writer=writeTextFile, readerName="file.read"):
    filename = varName + "." + extension
    return (varName + " = " + readerName + "(" + repr(filename) + ")", varName)

def storeAsPickle(self, varName, extension="in_pickle"):
    storeAsFile(self, varName, extension, writer=pickle.dump, readerName="pickle.load")

def printResumption(logger, func, args, kwargs):
    print("printResumption args: ", args, "kwargs: ", kwargs)
    code = func.__code__
    varDecls   = []
    formalArgs = []
    print("func:", dir(func))
    print("code:", dir(func.__code__))
    print("ARGS... ", code.co_varnames, code.co_argcount, args, kwargs)
    argNames = code.co_varnames[:code.co_argcount]
    print("argNames: ", argNames, " arg values: ", args)
    print(list(zip(argNames, args)))
    #print(kwargs.items())
    namedArgs = list(zip(code.co_varnames[:code.co_argcount], args)) + list(kwargs.items())
    for (argName, argValue) in namedArgs:
        (varDecl, formalArg) = store(argName, argValue)
        varDecls.append(varDecl)
        formalArgs.append(formalArg)
    call = func.__qualname__ + "(" + ",".join(formalArgs) + ")"
    print("CALL:", call)
    logger("\n".join([call] + varDecls))

def store(argName, argValue):
    if hasattr(argValue, "store"):
        argValue.store(argName)
    else:
        primTypes = [int, float, str]
        if type(argValue) in primTypes:
            r = repr(argValue)
            if len(r) < MAX_ARG_STRING:
                return storeAsString(argValue, argName)
            else:
                return storeAsVar   (argValue, argName)
        else:
            return storeAsPickle    (argValue, argName)


def resumable(logger=print):
    def _wrapped(func, *args, **kwargs):
        try:
            print("args: ", args, "kwargs: ", kwargs)
            func(*args, **kwargs)
        except Exception:
            print("RESUMPTION:::")
            printResumption(logger, func, args, kwargs)
            raise
    return decorator(_wrapped)
    #result.__qualname__ = func.__qualname__

class Storable(object):
    def extension(self):
        return "in"
    def store(self, testName, argName):
        varName = testName + "_" + argName
        result = self.stored()
        if   len(result) < MAX_ARG_STRING:
            return ("", result)
        elif len(result) < MAX_DATA_STRING:
            return (varName + "=" + result, varName)
        else:
            filename = varName + "." + self.extension()
            storeToFile(self, filename)
            return (varName + " = pickle.load(" + repr(filename) + ")", varName)
    def storeToFile(self, filenameSeed):
        raise NotImplementedError
    def stored(self):
        raise NotImplementedError

class TextStorable(object):
    storableExtension = "in"
    def storeToFile(self, filenameSeed):
        if self.isBinaryStorable():
          filename = varName + ".in_pickle"
          pickle.dump(self, filename)
        else:
          filename = varName + ".in"
          with open(filename, "w") as outf:
            outf.write(self.stored())

class BinStorable(object):
    def filenameExtension():
      return "in_pickle"
    def store(self, testName, argName):
        pass

if __name__ == "__main__":
    @resumable()
    def sampleFun(alpha, beta="default string"):
        print(alpha, beta)
        return len(beta)
    sampleFun(1)    # does nothing (finishes correctly)
    sampleFun(2, 3) # should print exception and its resumption

