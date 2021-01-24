'''
Copyright   : (c) Jean-Christophe Mincke, 2021

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
'''

from functools import partial

from typing import (Callable, TypeVar, Generic, Union,
                    IO, Any, Text, Type)

import typing as t

import numbers

import yaml
import json


a = TypeVar('a')
b = TypeVar('b')


class Status(Generic[a]):

    _path: t.List[Text] = []

    def message(self):
        return ""

    def path(self):
        return self._path


class StatusMissingField(Status[a]):

    def __init__(self, path: t.List[Text], field: Text) -> None:
        self._path = path
        self.__field = field

    def message(self):
        return "Missing field: {f}".format(f=self.__field)


class StatusOk(Status[a]):

    def __init__(self: 'StatusOk[a]', value: a) -> None:
        self.value = value

    def message(self):
        return "Success"


class StatusBadType(Status[a]):

    def __init__(self, path: t.List[Text],
                 expected_type: Type,
                 actual_value: a) -> None:
        self._path = path
        self.__expected_type = expected_type
        self.__actual_value = actual_value

    def message(self):
        return "Bad Type: expected type {e} but read value '{v}'"             \
               .format(e=self.__expected_type, v=self.__actual_value)


class StatusOneOfNoDecoder(Status[a]):

    def __init__(self, path: t.List[Text]) -> None:
        self._path = path

    def message(self):
        return "one_of: no valid decoder found"


class StatusNok(Status[a]):

    def __init__(self, path: t.List[Text], msg: Text) -> None:
        self._path = path
        self.__msg = msg

    def message(self):
        return self.__msg


class Decoder(Generic[a]):
    '''A Decoder class that simply wraps a decoding function.
    '''

    def __init__(self: 'Decoder[a]',
                 f: Callable[[t.List[str], Any], Status[a]]):

        self.__unDecode = f

    def at(self: 'Decoder[a]', path: t.List[str], value: Any) -> Status[a]:
        '''Apply `self` to a path and dictionary.

        Args:
            self: The Decoder to use to decode `value`.
            path: The current path in the document.
            value: The value to decode.
        '''
        return self.__unDecode(path, value)

    def __mul__(self: 'Decoder[Callable[[a], b]]',
                decoder: 'Decoder[a]') -> 'Decoder[b]':
        ''' Build a new Decoder that:

        - Applies `self` which is expected to return a
           function `f` that takes at least [1..n] arguments.
        - Partially apply `f` to the value returned by `decoder`.
            That partial application returns a function `g`.

        Args:
            self: A Decoder that must return a function.
            decoder: The Decoder that yields the next argument to `f`.

        '''
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

    def __matmul__(self: 'Decoder[Callable[[a], b]]',
                   decoder: 'Decoder[a]') -> 'Decoder[b]':
        ''' Build a new Decoder that:

        - Applies `self` which is expected to return a
           function `f` that takes at least [1..n] arguments.
        - Partially apply `f` to the value returned by `decoder`.
            That partial application returns a function `g`.
        - Call `g()`

        Args:
            self: A Decoder that must return a function `f`.
            decoder: The Decoder that yields the next argument to `f`.

        '''

        def decode(path, dic):
            rf = self.__mul__(decoder).at(path, dic)
            if type(rf) is StatusOk:
                return StatusOk(rf.value())
            else:
                return rf
        return Decoder(decode)

    def then(self: 'Decoder[a]',
             f: Callable[[a], 'Decoder[b]']) -> 'Decoder[b]':
        '''Create a Decoder that:

        - Applies `self`, yielding a value `v`.
        - Constructs a new Decoder by calling `f(v)`.

        Args:
            f: A function that takes a value and returns a new Decoder.

        '''
        def decode(path, dic):
            ra = self.at(path, dic)
            if type(ra) is StatusOk:
                return f(ra.value).at(path, dic)
            else:
                return ra

        return Decoder(decode)


def fail(msg: Text) -> Decoder[Any]:
    '''A decoder that always fails with a specific error message.

    Args:
        msg: The error message.

    '''

    def decode(path, dic):
        return StatusNok(path, msg)

    return Decoder(decode)


def succeed(v: a) -> Decoder[a]:
    '''A decoder that always succeeds and returns the given value.

    Args:
        v: The value inconditionally returned by the Decoder.

    '''

    def decode(path, dic):
        return StatusOk(v)

    return Decoder(decode)


def parse_yaml(doc: Union[str, IO[str]], decoder: Decoder[a]) -> a:
    '''
    Decode the given yaml document with the given Decoder.

    Raises a ValueError if the Decoder fails.

    Args:
        doc: The document to decode.
        decoder: The Decoder used to decode `doc`.

    Returns:
        The value yielded by `decoder`.
    '''
    dic = yaml.load(doc, Loader=yaml.FullLoader)
    r = decoder.at([], dic)
    if isinstance(r, StatusOk):
        return r.value
    else:
        raise ValueError("{e} in path '{p}'".format(e=r.message(), p=r.path))


def parse_json(str, decoder: Decoder[a]) -> a:
    '''
    Decode the given json document with the given Decoder.

    Raise a ValueError if the Decoder fails.

    Args:
        doc: The document to decode (string).
        decoder: The Decoder used to decode `doc`.

    Returns:
        The value yielded by `decoder`.
    '''
    dic = json.loads(str)
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


def nullable(decoder: Decoder[a], default: a) -> Decoder[a]:
    '''A Decoder to decode a potentially null value.

    It look at the value to decode. If it is null,
    it returns the specified default value.

    Otherwise, the given Decoder is applied.

    Args:
        decoder: The Decoder to apply if the value to decode is not null.
        default: The value returned if the value to decode is null.
    '''
    def decode(path, dic):
        if dic is None:
            return StatusOk(default)
        else:
            return decoder.at(path, dic)

    return Decoder(decode)


def null(value: a) -> Decoder[a]:
    '''Decode a null value into the given value.

    Raise a ValueError if the value is not a null value.

    Args:
        value: The value to return if the value to decode is null.

    '''
    def decode(path, dic):
        if dic is None:
            return StatusOk(value)
        else:
            return StatusBadType(path, 'Null', value)

    return Decoder(decode)


def field(field_name: Text, decoder: Decoder[a]) -> Decoder[a]:
    '''Decode specific field in a json/yaml object.

    Raise a ValueError if the field does not exist or the Decoder fails.

    Args:
        field_name: The name of the expected field.
        decoder: The Decoder to decode the field value.

    Returns:
        The value returned by `decoder`.
    '''
    def decode(path, dic):
        if field_name in dic:
            v = dic[field_name]
            path.append(field_name)
            return decoder.at(path, v)
        else:
            return StatusMissingField(path, field_name)

    return Decoder(decode)


def optional_field(field_name: Text, decoder: Decoder[a],
                   default: a) -> Decoder[a]:
    '''Decode a potentially missing field.

    The Decoder returns the given default value if the field does not exist.

    Raise a ValueError if the Decoder fails.

    Args:
        field_name: The name of the expected field.
        decoder: The Decoder to decode the field value.
        default: The value to return if the field does not exist.
    '''

    def decode(path, dic):
        if field_name in dic:
            v = dic[field_name]
            path.append(field_name)
            return decoder.at(path, v)
        else:
            return StatusOk(default)

    return Decoder(decode)


def List(decoder: Decoder[a]) -> Decoder[t.List[a]]:
    '''Decode a list of values into a python list.

    The given decoder is used to decode the elements of the list.

    Raise a ValueError if the Decoder fails on any element of the list.

    Args:
        decoder: The Decoder to decode the elements of the list .
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


def one_of(decoders: t.List[Decoder[a]]) -> Decoder[a]:
    '''Creates a Decoder that applies the given Decoders one by one
    and returns the value returned by the first successfull Decoder.

    Fails if no Decoder succeeds.

    Args:
        decoders: A list of Decoders.
    '''
    def decode(path, dic):
        for decoder in decoders:
            ra = decoder.at(path, dic)
            if type(ra) is StatusOk:
                return ra
        return StatusOneOfNoDecoder(path)

    return Decoder(decode)


Int: Decoder[int] = Decoder(__decode_int)
''' Decode a json/yaml integer into an int.
'''

Str: Decoder[str] = Decoder(__decode_str)
''' Decode a json/yaml string into a str.
'''

Bool: Decoder[bool] = Decoder(__decode_bool)
''' Decode a json/yaml boolean into a bool.
'''

Float: Decoder[float] = Decoder(__decode_float)
''' Decode a json/yaml float into a float.
'''

Real: Decoder[numbers.Real] = Decoder(__decode_real)
''' Decode a json/yaml number into a float or an int.
'''


def mapn(f: Callable[..., a], *decoders: Decoder) -> Decoder[a]:
    '''Creates a Decoder that applies the given Decoders in sequence
    and then pass their results (`v1`, `v2`, ..., `vn`) to the function `f`.
    The Decoder returns the results of `f(v1, v2, ..., vn)`.

    Args:
        f: A function with as many arguments as the number of Decoders.
        *decoders: Decoders to be applied in sequence.
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


noop: Decoder[Any] = Decoder(lambda path, dic: StatusOk(dic))
'''Decoder that returns the value to decode, unchanged.
'''


def lazy(f: Callable[[], Decoder[a]]) -> Decoder[a]:
    '''Create a Decoder that lazily builds another Decoder.

    Args:
        f: A factory For the lazily built Decoder.
    '''
    def decode(path, dic):
        decoder = f()
        return decoder.at(path, dic)

    return Decoder(decode)
