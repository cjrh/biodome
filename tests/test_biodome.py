import os
import sys

from copy import deepcopy
from uuid import uuid4

import pytest
import biodome


PY2 = sys.version_info < (3, 0)


def test_missing():
    assert biodome.biodome('BLAH') is None


def test_missing_default():
    assert biodome.biodome('BLAH', None) is None


@pytest.mark.parametrize('name,default,setting,result', [
    ('X', 2, '123', 123),
    ('X', '2', '123', '123'),
    ('X', True, '123', False),
    ('X', True, '', False),
    ('X', True, '0', False),
    ('X', True, 't', True),
    ('X', True, '1', True),
    ('X', True, 'y', True),
    ('X', True, 'yes', True),
    ('X', True, 'YES', True),
    ('X', True, 'Yes', True),
    ('X', True, 'Y', True),
    ('X', True, 'True', True),
    ('X', True, 'true', True),
    ('X', True, 'TRUE', True),
    ('X', True, 'on', True),
    ('X', True, 'On', True),
    ('X', True, 'ON', True),
    ('X', True, 'active', True),
    ('X', True, 'ACTIVE', True),
    ('X', True, 'Active', True),
    ('X', False, 'y', True),
    ('X', False, 'yes', True),
    ('X', False, 'YES', True),
    ('X', False, 'Yes', True),
    ('X', False, 'Y', True),
    ('X', False, 'True', True),
    ('X', False, 'true', True),
    ('X', False, 'TRUE', True),
    ('X', False, 'on', True),
    ('X', False, 'On', True),
    ('X', False, 'ON', True),
    ('X', False, 'active', True),
    ('X', False, 'ACTIVE', True),
    ('X', False, 'Active', True),

    ('X', False, 'yas', False),
    ('X', False, 'blah', False),
    ('X', False, '123', False),
    ('X', False, '____', False),
    ('X', False, 'heyy', False),

    ('X', 123, 'heyy', 123),
    ('X', -123, '-123', -123),
    ('X', 0, '0', 0),

    ('X', 0.1, '0', 0),
    ('X', 0.1, '1.2', 1.2),
    ('X', -0.1, '-1.2', -1.2),
    ('X', 1, '1.0', 1),

    ('X', 'heya', 'blah', 'blah'),

    ('X', {}, '{"a": 1}', dict(a=1)),
    ('X', {}, '{"a": "blah", "b": "bleh"}', dict(a='blah', b='bleh')),

    ('X', [], '[1, 2, 3]', [1, 2, 3]),
    ('X', [], '[]', []),
    ('X', [], '[', []),
    ('X', [], '[blah]', []),
    ('X', [], '["blah"]', ['blah']),

    ('X', (1, 2), 'blah', (1, 2)),
    ('X', (), 'blah', ()),
    ('X', (), '(1, 2)', (1, 2)),
    ('X', (), '(1,2)', (1, 2)),
    ('X', (), '(   1   ,   2   )', (1, 2)),
    ('X', (), '(1)', ()),
    ('X', (), '(1,)', (1,)),

    ('X', '0', '1.053', '1.053'),
])
def test_param_set(name, default, setting, result):
    os.environ[name] = str(setting)
    assert biodome.biodome(name, default) == result


@pytest.mark.skipif(PY2, reason="requires Python 3+")
@pytest.mark.parametrize('name,default,setting,result', [
    ('X', {1, 2, 3}, '{1, 2}', {1, 2}),
    ('X', {1, 2, 3}, '{"1":2}', {1, 2, 3}),
])
def test_param(name, default, setting, result):
    """ast.literal_eval is only supported in Python 3"""
    os.environ[name] = str(setting)
    assert biodome.biodome(name, default) == result


@pytest.mark.parametrize('name,cast,setting,result', [
    ('X', bool, 'blah', False),
    ('X', bool, '1', True),
    ('X', bool, '0', False),
    ('X', bool, 'True', True),
    ('X', bool, 'False', False),
    ('X', bool, 'true', True),
    ('X', bool, 'false', False),

    ('X', float, 'blah', None),
    ('X', float, '1', 1.0),
    ('X', float, '1', 1),
    ('X', float, '1e-17', 1e-17),

    ('X', int, 'blah', None),
    ('X', int, '1', 1),
    ('X', int, '1.0', None),

    ('X', str, '1.0', '1.0'),
    ('X', str, '1', '1'),

    ('X', list, '1', None),
    ('X', list, '[1]', [1]),

    ('X', dict, '{"a": 123}', dict(a=123)),
])
def test_cast(name, cast, setting, result):
    os.environ[name] = str(setting)
    assert biodome.biodome(name, cast=cast) == result


@pytest.mark.skipif(PY2, reason="requires Python 3+")
@pytest.mark.parametrize('name,cast,setting,result', [
    ('X', set, '{2}', {2}),
])
def test_cast_set(name, cast, setting, result):
    os.environ[name] = str(setting)
    assert biodome.biodome(name, cast=cast) == result


@pytest.mark.parametrize('name,default,setting,result', [
    ('X', [], 'list(1,2,3)', [1, 2, 3]),
    ('X', set(), 'set([2])', {2}),
    ('X', {}, 'dict(a=1)', {"a": 1}),
])
def test_noeval(name, default, setting, result):
    """Verify that no code evaluation occurs"""
    os.environ[name] = str(setting)
    assert biodome.biodome(name, default=default) != result
    assert biodome.biodome(name, default=default) == default


def test_environ_set():
    assert 'blah' not in os.environ
    biodome.environ['blah'] = '123'
    assert 'blah' in os.environ
    assert os.environ.get('blah') == '123'
    del biodome.environ['blah']
    assert 'blah' not in os.environ


def test_environ_int():
    assert not os.environ.get('blah')
    biodome.environ['blah'] = 123

    # Both ways work
    assert os.environ['blah'] == '123'
    assert biodome.environ['blah'] == '123'

    # NOTE: we get an int out because the default is type int
    assert biodome.environ.get('blah', default=0) == 123

    del biodome.environ['blah']
    assert 'blah' not in os.environ


def test_environ_types():
    assert not os.environ.get('blah')
    biodome.environ['blah'] = dict(a=[1, 2, 3])

    rep = "{'a': [1, 2, 3]}"

    # Both ways work - old and new
    assert os.environ['blah'] == rep
    assert biodome.environ['blah'] == rep

    # NOTE: we get an int out because the default is type int
    assert biodome.environ.get('blah', default={}) == dict(a=[1, 2, 3])

    del biodome.environ['blah']
    assert 'blah' not in os.environ


def test_callable():
    assert not os.environ.get('MY_SETTING')
    biodome.environ['MY_SETTING'] = dict(a=[1, 2, 3])
    MY_SETTING = biodome.environ.get_callable('MY_SETTING', {})
    assert MY_SETTING() == dict(a=[1, 2, 3])


def test_callable_int():
    os.environ['MY_SETTING2'] = '5'
    MY_SETTING2 = biodome.environ.get('MY_SETTING2')
    assert MY_SETTING2 == '5'


def test_env_changer_new():
    assert 'BLAH' not in biodome.environ

    with biodome.env_change('BLAH', 123):
        assert biodome.environ.get('BLAH', 0) == 123

    assert 'BLAH' not in biodome.environ


def test_env_changer_existing():
    biodome.environ['BLAH'] = 456

    with biodome.env_change('BLAH', 123):
        assert biodome.environ.get('BLAH', 0) == 123

    assert biodome.environ.get('BLAH', 0) == 456
    del biodome.environ['BLAH']


def test_loading_file(tmpdir):
    p = tmpdir.join(str(uuid4()) + '.env')
    p.write_text(u'# This is a comment\nX_SET=123', 'utf8')
    expected = deepcopy(biodome.environ.data)
    expected['X_SET'] = '123'

    biodome.load_env_file(str(p))
    actual = biodome.environ.data
    assert actual == expected
    assert biodome.environ.get('X_SET', 1) == 123


def test_loading_missing_file(tmpdir):
    p = str(tmpdir) + str(uuid4()) + '.env'
    before = deepcopy(biodome.environ.data)
    biodome.load_env_file(str(p))
    assert biodome.environ.data == before


def test_loading_missing_file_raises(tmpdir):
    p = str(tmpdir) + str(uuid4()) + '.env'
    before = deepcopy(biodome.environ.data)
    with pytest.raises(IOError):
        biodome.load_env_file(str(p), raises=True)
    assert biodome.environ.data == before
