
from functools import partial

import yaml

class StatusMissingField:

    def __init__(self, field):
        self.field = field

    def message(self):
        return "Missing field: {f}".format(f=self.field)

class StatusOk:

    def __init__(self, value):
        self.value = value

    def message(self):
        return "Success"

class StatusBadType:

    def __init__(self, expected_type, actual_value):
        self.expected_type = expected_type
        self.actual_value = actual_value

    def message(self):
        return "Bad Type: expected type {e} but read value '{v}'".format(e=self.expected_type, v=self.actual_value)

class StatusOneOfNoDecoder:

    def message(self):
        return "one_of: no valid decoder found"

class StatusNok:

    def __init__(self, msg):
        self.msg = msg

    def message(self):
        return self.msg



class Decoder:

    unDecode = None

    def __init__(self, f):
        self.unDecode = f

    def __mul__(self, decoder):

        def decode(dic):
            rf = self.unDecode(dic)
            if type(rf) is StatusOk:
                ra = decoder.unDecode(dic)
                if isinstance(ra, StatusOk):
                    return StatusOk(partial(rf.value, ra.value))
                else:
                    return ra
            else:
                return rf
        return Decoder(decode)

    def __matmul__(self, decoder):

        def decode(dic):
            rf = self.__mul__(decoder).unDecode(dic)
            if type(rf) is StatusOk:
                print(rf.value)
                return StatusOk(rf.value())
            else:
                return rf
        return Decoder(decode)

    def then(self, f):

        def decode(dic):
            ra = self.unDecode(dic)
            print(ra)
            print(ra.value)
            if type(ra) is StatusOk:
                print(f(ra.value))
                return f(ra.value).unDecode(dict)
            else:
                return ra

        return Decoder(decode)

def succeed(v) : return pure(v)

def fail(msg) :

    def decode(dic): return StatusNok(msg)

    return Decoder(decode)

def pure(v):

    def decode(dic): return StatusOk(v)

    return Decoder(decode)


def field(field_name, decoder):

    def decode(dic) :
        if field_name in dic:
            v = dic[field_name]
            return decoder.unDecode(v)
        else:
            return StatusMissingField(field_name)

    return Decoder(decode)

def parse_string(str, decoder):
    dic = yaml.load(doc, Loader=yaml.FullLoader)
    print(dic)
    r = decoder.unDecode(dic)
    if isinstance(r, StatusOk):
        return r.value
    else:
        raise ValueError(r.message())


def decode_int(v):
    if type(v) is int:
        return StatusOk(v)
    else:
        return StatusBadType('int', v)

def decode_str(v):
    if type(v) is str:
        return StatusOk(v)
    else:
        return StatusBadType('str', v)


def decode_bool(v):
    if type(v) is bool:
        return StatusOk(v)
    else:
        return StatusBadType('bool', v)


def decode_float(v):
    if type(v) is float:
        return StatusOk(v)
    else:
        return StatusBadType('float', v)

def decode_null(v):
    if v is None:
        return StatusOk(v)
    else:
        return StatusBadType('None', v)


def nullable(decoder):

    def decode(dic):
        if dic is None:
            return StatusOk(None)
        else:
            return decoder.unDecode(dic)

    return Decoder(decode)




def field(field_name, decoder):

    def decode(dic) :
        if field_name in dic:
            v = dic[field_name]
            return decoder.unDecode(v)
        else:
            return StatusMissingField(field_name)

    return Decoder(decode)

def optional_field(field_name, decoder, default=None):

    def decode(dic) :
        if field_name in dic:
            v = dic[field_name]
            return decoder.unDecode(v)
        else:
            return StatusOk(default)

    return Decoder(decode)



def List(decoder):

    def decode(l):
        if type(l) is list:
            rl = []
            for ra in map(decoder.unDecode, l):
                if type(ra) is StatusOk:
                    rl.append(ra.value)
                else:
                    return ra
            return StatusOk(rl)
        else:
            return StatusBadType("list", l)



    return Decoder(decode)

def one_of(decoders):

    def decode(dic):
        for decoder in decoders:
            ra = decoder.unDecode(dic)
            if type(ra) is StatusOk:
                return ra
        return StatusOneOfNoDecoder()

    return Decoder(decode)


Int = Decoder(decode_int)
Str = Decoder(decode_str)
Bool = Decoder(decode_bool)
Float = Decoder(decode_float)
Null = Decoder(decode_null)


def mapn(f, *decoders):
    def decode(dic):
        ras = []
        for decoder in decoders:
            ra = decoder.unDecode(dic)
            if type(ra) is StatusOk:
                ras.append(ra.value)
            else:
                return ra
        return StatusOk(f(*ras))

    return Decoder(decode)
