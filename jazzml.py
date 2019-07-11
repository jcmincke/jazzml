
from functools import partial

import numbers

import yaml


class StatusMissingField:

    def __init__(self, path, field):
        self.path = path
        self.field = field

    def message(self):
        return "Missing field: {f}".format(f=self.field)

class StatusOk:

    def __init__(self, value):
        self.value = value

    def message(self):
        return "Success"

class StatusBadType:

    def __init__(self, path, expected_type, actual_value):
        self.path = path
        self.expected_type = expected_type
        self.actual_value = actual_value

    def message(self):
        return "Bad Type: expected type {e} but read value '{v}'".format(e=self.expected_type, v=self.actual_value)

class StatusOneOfNoDecoder:

    def __init__(self, path):
        self.path = path

    def message(self):
        return "one_of: no valid decoder found"

class StatusNok:

    def __init__(self, path, msg):
        self.path = path
        self.msg = msg

    def message(self):
        return self.msg



class Decoder:
    '''Main Decoder class
    '''
    __unDecode = None

    def __init__(self, f):
        self.__unDecode = f

    def at(self, path, dic): return self.__unDecode(path, dic)

    def __mul__(self, decoder):

        def decode(path, dic):
            rf = self.at(path, dic)
            if type(rf) is StatusOk:
                ra = decoder.at(path, dic)
                if isinstance(ra, StatusOk):
                    return StatusOk(partial(rf.value, ra.value))
                else:
                    return ra
            else:
                return rf
        return Decoder(decode)

    def __matmul__(self, decoder):

        def decode(path, dic):
            rf = self.__mul__(decoder).at(path, dic)
            if type(rf) is StatusOk:
                return StatusOk(rf.value())
            else:
                return rf
        return Decoder(decode)

    def then(self, f):
        ''' Create a Decoder that depends on previous results.
        '''
        def decode(path, dic):
            ra = self.at(path, dic)
            if type(ra) is StatusOk:
                return f(ra.value).at(path, dict)
            else:
                return ra

        return Decoder(decode)

def fail(msg) :
    '''A decoder that always fails with a specific error message.
    '''

    def decode(path, dic): return StatusNok(path, msg)

    return Decoder(decode)

def succeed(v):
    '''A decoder that always succeeds and returns the given value.
    '''

    def decode(path, dic): return StatusOk(v)

    return Decoder(decode)



def parse_yaml(str, decoder):
    dic = yaml.load(str, Loader=yaml.FullLoader)
    r = decoder.at([], dic)
    if isinstance(r, StatusOk):
        return r.value
    else:
        raise ValueError("{e} in path '{p}'".format(e=r.message(), p=r.path))


def __decode_int(path, v):
    if type(v) is int:
        return StatusOk(v)
    else:
        return StatusBadType(path, 'int', v)

def __decode_str(path, v):
    if type(v) is str:
        return StatusOk(v)
    else:
        return StatusBadType(path, 'str', v)


def __decode_bool(path, v):
    if type(v) is bool:
        return StatusOk(v)
    else:
        return StatusBadType(path, 'bool', v)


def __decode_float(path, v):
    if type(v) is float:
        return StatusOk(v)
    else:
        return StatusBadType(path, 'float', v)

def __decode_real(path, v):
    if isinstance(v, numbers.Real):
        return StatusOk(v)
    else:
        return StatusBadType(path, 'real', v)


def __decode_null(path, v):
    if v is None:
        return StatusOk(v)
    else:
        return StatusBadType(path, 'None', v)


def nullable(decoder, default = None):

    def decode(path, dic):
        if dic is None:
            return StatusOk(default)
        else:
            return decoder.at(path, dic)

    return Decoder(decode)


def null(value=None):
    '''Decode a null value into the given python value.
    '''
    def decode(path, dic):
        if dic is None:
            return StatusOk(value)
        else:
            return StatusBadType(path, 'Null', value)

    return Decoder(decode)


def field(field_name, decoder):
    '''Decode specific field in a json/yaml object.
    '''
    def decode(path, dic) :
        if field_name in dic:
            v = dic[field_name]
            path.append(field_name)
            return decoder.at(path, v)
        else:
            return StatusMissingField(path, field_name)

    return Decoder(decode)

def optional_field(field_name, decoder, default=None):
    '''Decode specific field in a json/yaml object.
    Returns a default value if the field does not exist.
    '''

    def decode(path, dic) :
        if field_name in dic:
            v = dic[field_name]
            path.append(field_name)
            return decoder.at(path, v)
        else:
            return StatusOk(default)

    return Decoder(decode)



def List(decoder):
    '''Decoder json/yaml list a list of values to a python list.
    The given decoder is use used to decode the elements of the list
    '''

    def decode(path, l):
        if type(l) is list:
            rl = []
            for ra in map(partial(decoder.at, path), l):
                if type(ra) is StatusOk:
                    rl.append(ra.value)
                else:
                    return ra
            return StatusOk(rl)
        else:
            return StatusBadType(path, "list", l)



    return Decoder(decode)

def one_of(decoders):
    '''Apply the given decoders one by one and return the value produced
    by the first successfull decoder.
    Fails if no decoder succeeds.
    '''
    def decode(path, dic):
        for decoder in decoders:
            ra = decoder.at(path, dic)
            if type(ra) is StatusOk:
                return ra
        return StatusOneOfNoDecoder(path)

    return Decoder(decode)


Int = Decoder(__decode_int)
''' Decode a json/yaml integer into an int.
'''

Str = Decoder(__decode_str)
''' Decode a json/yaml string into an str.
'''

Bool = Decoder(__decode_bool)
''' Decode a json/yaml boolean into an bool.
'''

Float = Decoder(__decode_float)
''' Decode a json/yaml float into an float.
'''

Real = Decoder(__decode_real)
''' Decode a json/yaml number into an float or an int.
'''



def mapn(f, *decoders):
    '''Apply the given decoders and then pass their results to the given function.
    '''
    def decode(path, dic):
        ras = []
        for decoder in decoders:
            ra = decoder.at(path, dic)
            if type(ra) is StatusOk:
                ras.append(ra.value)
            else:
                return ra
        return StatusOk(f(*ras))

    return Decoder(decode)

as_dict = Decoder(lambda path, dic: StatusOk(dic))
'''decode the json/yaml document into a dict.
'''


def lazy(f):

    def decode(path, dic):
        decoder = f()
        return decoder.at(path, dic)

    return Decoder(decode)