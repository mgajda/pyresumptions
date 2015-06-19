#!/usr/bin/python3

from   decorator import decorator
from   inspect   import getfullargspec
import pickle

MAX_ARG_STRING  = 20
MAX_DATA_STRING = 80

# Storing variables
def storeAsString(self, varName):
  return (""                          , varName + "=" + repr(self))

def storeAsVar(self, varName):
  return (varName + " = " + repr(self), varName                   )

def writeTextFile(self, filename):
    with open(filename, "w") as outf:
        outf.write(repr(self))

def storeAsFile(self, varName, extension="in", writer=writeTextFile, readerName="file.read"):
    filename = varName + "." + extension
    return (varName + " = " + readerName + "(" + repr(filename) + ")", varName)

def storeAsPickle(self, varName, extension="in_pickle"):
    storeAsFile(self, varName, extension, writer=pickle.dump, readerName="pickle.load")

#def indentedPrint(*args, indent=2, aPrint=print):
#    aPrint(" "*indent, *args)

def printResumption(func, args, kwargs, logger=print):
    "Prints a resumption: function call with all its arguments."
    code = func.__code__
    varDecls   = []
    formalArgs = []
    argNames = code.co_varnames[:code.co_argcount]
    namedArgs = (list(zip(code.co_varnames[:code.co_argcount], args)) +
                 list(kwargs.items()))
    for (argName, argValue) in namedArgs:
        (varDecl, formalArg) = store(argValue, argName)
        varDecls.append(varDecl)
        formalArgs.append(formalArg)
    call = func.__qualname__ + "(" + ",".join(formalArgs) + ")"
    varDecls.append(call)
    logger("\n".join(varDecls))

def store(argValue, argName):
    if hasattr(argValue, "store"):
        return argValue.store(argName)
    else:
        return _store(argValue, argName)

def storedFileExtension(argValue):
    if hasattr(argValue, "storedFileExtension"):
        return   argValue.storedFileExtension(argName)
    else:
        if type(argValue) in _typesStoredAsRepr:
            return   "in"
        else:
            return   "in_pickle"

"Primitive types (those without .store method), which can be stored directly as their repr."
_typesStoredAsRepr = [int, float, str]

def _store(argValue, argName):
    "Store a primitive type (one of these that cannot have .store method added.)"
    global _typesStoredAsRepr
    if type(argValue) in _typesStoredAsRepr:
        r = repr(argValue)
        if len(r) < MAX_ARG_STRING:
            return storeAsString(argValue, argName)
        else:
            return storeAsVar   (argValue, argName)
    else:
        return     storeAsPickle(argValue, argName)

def checkpoint(logger=print):
    "Checkpoint the function call upon each run, so that it may be resumed."
    def _wrapped(func, *args, **kwargs):
         printResumption(func, args, kwargs, logger=logger)
         func(*args, **kwargs)
    return decorator(_wrapped)

def resumable(logger=print):
    "This function is resumable upon exception."
    def _wrapped(func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            printResumption(logger, func, args, kwargs)
            raise
    return decorator(_wrapped)

class Storable(object):
    def extension(self):
        return "in"
    def stored(self):
        return pickle.dumps(self)
    # FIXME: testName in store()
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

if __name__ == "__main__":
    print ("Unit testing resumptions.")
    def sampleFun(alpha, beta="default string"):
        print("Executing sampleFun: ", alpha, beta)
        return len(beta)
    aResumable  = resumable ()(sampleFun)
    aCheckpoint = checkpoint()(sampleFun)
    aResumable(1, "eeee")    # does nothing (finishes correctly)
    try:
        aResumable(2, 3) # should print exception and its resumption
        raise NotImplementedError()
    except:
        pass # correct behaviour
    _mediumString = "alphabetic, but not frenetic, crowdy, but not bawdy, exceptional, and not geminal"
    _longString   = 3*_mediumString
    aCheckpoint(_mediumString, _longString)

