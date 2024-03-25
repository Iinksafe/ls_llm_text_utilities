from unicodedata import category
from secrets import randbelow
from .classes import *


def bits(int: int): return (7 + int.bit_length()) // 8


def scramble(data: Any, /, *, output: tuple[Any, ...] = ()) -> tuple[Any, ...]:
    while data:
        char = randbelow(len(data))
        output += data[char],
        data = data[:char] + data[1 + char:]
    return output


def tokenize(text: str, /, *, j: MethodType = ''.join) -> map:
    tokens = [text[0]],
    for token in text[1:]:
        if category(token) != category(tokens[-1][-1]): tokens += [token],
        else: tokens[-1].append(token)
    return map(j, tokens)


__all__ = ['bits', 'scramble', 'tokenize', 'GenerationError', 'AI', 'LLM', 'Cipher']
