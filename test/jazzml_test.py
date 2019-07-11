

import hypothesis.strategies as hp

from functools              import reduce
from hypothesis             import given, settings, event, assume, PrintSettings, reproduce_failure
from hypothesis.strategies  import text, integers, floats, booleans, lists, floats \
                                 , just, dictionaries, one_of
from math                   import isnan

import io
import tempfile as tf
import yaml


from jazzml import *


def gen_dictionary(depth):
    any_value = [integers(), text(), just(None), booleans(), floats(allow_nan=False), lists(integers(), 0, 10)]

    if depth > 0:
        any_value.append(gen_dictionary(depth-1))

    return dictionaries(text(), hp.one_of(any_value), dict, 0, 10)


def dict_depth(dic):
    if type(dic) is not dict:
        return 0
    depths = [dict_depth(dic[k])+1 for k in dic.keys()]
    if len(depths) == 0:
        return 0
    else:
        return max(depths)




def mk_parser(dic):

    def go(k):
        v = dic[k]
        print (v)
        vdec = None
        if v is None:
            event("None")
            vdec = null()
        elif type(v) is int:
            event("int")
            vdec = Int
        elif type(v) is str:
            event("str")
            vdec = Str
        elif type(v) is bool:
            event("bool")
            vdec = Bool
        elif type(v) is float:
            event("float")
            vdec = Float
        elif type(v) is list:
            event("list")
            vdec = List(Int)
        elif type(v) is dict:
            vdec = mk_parser(v)
        else:
            raise ValueError("bad value type: {v}".format(v=v))

        return field(k, vdec).then((lambda k : lambda v: succeed((k, v)))(k))

    decoders = [go(k) for k in dic.keys()]
    return mapn(lambda *vals: dict(vals), *decoders)


def mk_app_parser(dic):

    def go(k):
        v = dic[k]
        print (v)
        vdec = None
        if v is None:
            event("None")
            vdec = null()
        elif type(v) is int:
            event("int")
            vdec = Int
        elif type(v) is str:
            event("str")
            vdec = Str
        elif type(v) is bool:
            event("bool")
            vdec = Bool
        elif type(v) is float:
            event("float")
            vdec = Float
        elif type(v) is list:
            event("list")
            vdec = List(Int)
        elif type(v) is dict:
            vdec = mk_app_parser(v)
        else:
            raise ValueError("bad value type: {v}".format(v=v))

        return field(k, vdec).then((lambda k : lambda v: succeed((k, v)))(k))

    decoders = [go(k) for k in dic.keys()]

    if len(decoders) == 0:
        return succeed({})

    prefix_decs = [succeed(lambda *vals: dict(vals))] + decoders[:-1]
    last_dec = decoders[-1]

    parser = reduce(lambda d1, d2: d1 * d2, prefix_decs) @ last_dec

    return parser



@settings(print_blob=PrintSettings.ALWAYS)
@given(gen_dictionary(5))
def test_parser(dic):

    event("dict depth: {d}".format(d = dict_depth(dic)))

    parser = mk_parser(dic)

    status = parser.at([], dic)

    assert type(status) is StatusOk

    assert status.value == dic


@settings(print_blob=PrintSettings.ALWAYS)
@given(gen_dictionary(5))
def test_parser_yaml_doc(dic):

    event("dict depth: {d}".format(d = dict_depth(dic)))

    parser = mk_parser(dic)

    doc = yaml.dump(dic)

    r1 = parse_yaml(doc, parser)

    handle = tf.TemporaryFile()

    handle.write(doc.encode('ascii'))
    handle.seek(0)
    r2 = parse_yaml(handle, parser)

    assert r2 == dic
    handle.close()

@given(gen_dictionary(5))
def test_app_parser(dic):

    event("dict depth: {d}".format(d = dict_depth(dic)))

    parser = mk_app_parser(dic)

    status = parser.at([], dic)

    assert type(status) is StatusOk

    assert status.value == dic


any_value = [integers(), text(), just(None), booleans(), floats(), lists(integers(), 0, 10)]

@settings(print_blob=PrintSettings.ALWAYS)
@given(hp.one_of(any_value))
#@reproduce_failure('4.24.0', b'AAYA')
def test_one_of(v):
    assume(type(v) is not float or not isnan(v))
    print(v)
    print(type(v))


    parser = one_of([Int, Str, Bool, Float, List(Int), null()])

    status = parser.at([], v)

    assert type(status) is StatusOk

    assert status.value == v



@settings(print_blob=PrintSettings.ALWAYS)
@given(gen_dictionary(1), text(), integers())
def test_optional_field(dic, key, default):
    assume(len(dic) != 0)
    assume(not (key in dic.keys()))

    parser = optional_field(key, succeed(None), default=default)

    status = parser.at([], dic)

    assert type(status) is StatusOk

    assert status.value == default

    dic[key] = default + 1

    parser = optional_field(key, Int, default=default)

    status = parser.at([], dic)

    assert type(status) is StatusOk

    assert status.value == default + 1

'''
s = io.StringIO()

y=yaml.YAML()
yyaml.default_flow_style = False


yaml.dump({'a': [1, 2]}, s)

r = file("kk", r)

{'': nan} != {'': nan}
'''