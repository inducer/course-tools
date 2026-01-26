from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Sequence


# {{{ argmin, argmax

def argmin2(iterable, return_value=False):
    it = iter(iterable)
    try:
        current_argmin, current_min = next(it)
    except StopIteration:
        raise ValueError("argmin of empty iterable") from None

    for arg, item in it:
        if item < current_min:
            current_argmin = arg
            current_min = item

    if return_value:
        return current_argmin, current_min
    else:
        return current_argmin


def argmin(iterable):
    return argmin2(enumerate(iterable))

# }}}


# {{{ grade computation

def drop_lowest(values: Sequence[float]) -> Sequence[float]:
    idx = values.index(min(values))
    assert idx >= 0 and idx < len(values)
    result = list(values)
    del result[idx]
    return result


def count_none(values: Sequence[float]) -> int:
    result = 0
    for i in values:
        if i is None:
            result += 1

    return result


def drop_nones(values: Sequence[float | None]) -> Sequence[float]:
    return [i for i in values if i is not None]


def zero_none(v: float | None) -> float:
    return 0 if v is None else v


def zero_nones(values: Sequence[float | None]) -> Sequence[float]:
    return [0 if v is None else v for v in values]


def div_or_none(a: float | None, b: float) -> float | None:
    if a is None:
        return None
    else:
        return a/b


def weighted_avg(
        seq: Sequence[float | None], weights: Sequence[float],
        *,
        extra_seq: Sequence[float | None] = (),
        extra_weights: Sequence[float] = ()
        ) -> float:
    assert len(seq) == len(weights)
    assert len(extra_seq) == len(extra_weights)

    return (
            sum(zero_none(l_i)*w
                for w, l_i in zip(
                    list(weights) + list(extra_weights),
                    list(seq) + list(extra_seq), strict=False))
            / sum(weights))


def drop_weighted(
        seq: Sequence[float],
        weights: Sequence[float],
        drop_weight: float) -> tuple[Sequence[float], Sequence[float]]:
    assert len(seq) == len(weights)

    mseq = list(seq)
    mweights = list(weights)
    del seq
    del weights

    while drop_weight:
        drop_idx = argmin(mseq)
        w = mweights[drop_idx]
        if w > drop_weight:
            mweights[drop_idx] -= drop_weight
            drop_weight = 0
        else:
            drop_weight -= w
            del mseq[drop_idx]
            del mweights[drop_idx]

    return mseq, mweights


def test_drop_weighted():
    s, weights = drop_weighted([100, 80], [20, 10], drop_weight=5)
    assert s == [100, 80]
    assert weights == [20, 5]

    s, weights = drop_weighted([100, 80], [20, 10], drop_weight=15)
    assert s == [100]
    assert weights == [15]

    s, weights = drop_weighted([80, 100], [20, 10], drop_weight=15)
    assert s == [100]
    assert weights == [5]

# }}}


# {{{ formatting

def format_grade(v: float | None) -> str:
    if v is None:
        return "NONE"
    else:
        return "%.1f" % (v)


def format_frac(v: float | None) -> str:
    if v is None:
        return "NONE"
    else:
        return "%.1f" % (100*v)


def format_frac_list(lst: Sequence[float | None]) -> str:
    return ", ".join(format_frac(f) for f in lst)


def format_grade_list(lst: Sequence[float | None]) -> str:
    return ", ".join(format_grade(f) for f in lst)

# }}}


# {{{ drop_letter_grade

_LETTERS = "ABCDEF"
_LETTER_DROP_MAPPING = {
    f"{letter}{suffix}": f"{_LETTERS[i+1]}{suffix}"
    for i, letter in enumerate(_LETTERS[:-1])
    for suffix in ["+", "", "-"]
}


def drop_letter_grade(letter: str) -> str:
    result = _LETTER_DROP_MAPPING.get(letter)
    if result:
        return result
    elif letter in ["I", "F"]:
        return letter
    else:
        raise ValueError(f"unexpected letter grade: '{letter}")

# }}}

# vim: foldmethod=marker
