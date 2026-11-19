import pytest
from pymol import testing
from pymol import constants


def test_safe_alpha_list_eval():
    f = constants.safe_alpha_list_eval
    # expected use case
    assert f('[blue, red, green]') == ["blue", "red", "green"]
    # single item
    assert f('[AB]') == ["AB"]
    # trailing comma
    assert f('[A,]') == ["A"]
    # tuple
    assert f("('A',)") == ('A',)
    # single value
    assert f("('A')") == 'A'
    assert f("'A'") == 'A'
    # with quotes
    assert f('["AB", \'cd\']') == ["AB", "cd"]
    # str, int, non-alnum characters
    assert f('[A, 1, 2+3, B:C, D E, "F G"]') == ["A", 1, 23, "BC", "DE", "FG"]


def test_safe_eval():
    f = constants.safe_eval
    assert f('[AB]') == ["AB"]
    assert f('[A,]') == ["A"]
    assert f("('A',)") == ('A',)
    assert f("('A')") == 'A'
    assert f("'A'") == 'A'
    assert f('["AB", \'cd\']') == ["AB", "cd"]
    assert f('[A, 1, 2+3, "F G"]') == ["A", 1, 5, "F G"]
    assert f('()') == ()
    assert f('[]') == []
    assert f('{}') == {}
    assert f('{foo: bar}') == {"foo": "bar"}
    assert f('1 + 2') == 3
    with pytest.raises(TypeError):
        f('__import__("os").times()')
