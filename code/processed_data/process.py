#!/usr/bin/env python3
from tqdm import tqdm
from io import RawIOBase
import pudb

class Sexp:
    def __init__(self, ss, lloc, rloc):
        self.ss = ss
        self.lloc = lloc 
        self.rloc = rloc 
    def __str__(self):
        out = "("
        for s in self.ss:
            out += s.__str__()
            out += " "
        out += ")"
        return out


class Loc:
    def __init__(self, ix, line, col):
        self.ix = ix
        self.line = line 
        self.col = col
    def __str__(self):
        return f"{self.line}:{self.col}"


class Token:
    def __init__(self, raw, locl, locr):
        self.raw = raw 
        self.locl = locl
        self.locr = locr
    def __str__(self):
        return self.raw

class Atom(Token):
    pass

class CodeBlock(Token):
    pass

class Parser:
    def __init__(self, raw):
        self.raw = raw
        self.ix = 0
        self.line = 1
        self.col = 1

    @property
    def peek(self):
        assert self.ix <= len(self.raw)
        while self.ix < len(self.raw):
            c = self.raw[self.ix]
            if c == '\n':
                self.line += 1
                self.col = 1
                self.ix += 1
            elif c == ' ' or c == '\t': 
                self.col += 1
                self.ix += 1
            else:
                break
        if self.ix == len(self.raw): return None
        return self.raw[self.ix]
    @property
    def eof(self): 
        c = self.peek
        assert self.ix <= len(self.raw)
        return self.ix == len(self.raw)
    
    def eat_char(self):
        assert self.ix <= len(self.raw)
        if self.ix == len(self.raw): return 

        c = self.peek 
        if c == '\n':
            self.line += 1
            self.col = 1
        else: 
            self.col += 1
        self.ix += 1

    def eat_non_sexp(self):
        while self.peek is not None and self.peek != "(": self.eat_char()

    @staticmethod
    def is_whitespace(c):
        return c == ' ' or c == '\n' or c == '\t'
    
    @staticmethod
    def is_sigil(c):
        return c == '(' or c == ')' or c == '{' or c == '}'

    @property 
    def loc(self):
        return Loc(self.ix, self.line, self.col)

    def eat_atom(self):
        locl = self.loc
        while self.peek is not None and \
                not Parser.is_whitespace(self.peek) and \
                not Parser.is_sigil(self.peek):
            self.eat_char()
        locr = self.loc
        return Atom(self.raw[locl.ix:locr.ix], locl, locr)

    def eat_sigil(self):
        assert Parser.is_sigil(self.peek)
        return self.eat_char()

    @staticmethod
    def is_atom_start(c):
        return not Parser.is_whitespace(c) and not Parser.is_sigil(c)

    def eat_sexp(self, depth):
        # print(f'EAT @ {self.line}:{self.col}')

        if self.eof: return None

        if self.peek == '(':
            lloc = self.loc
            print('*' * depth + f'( @ {self.line}:{self.col}')
            self.eat_char()
            ss = []
            # print("."*depth)
            while self.peek != ")":
                if self.eof:
                    raise RuntimeError(f"unclosed '(' at {lloc}")
                # print(f'EATING @ {self.line}:{self.col}')
                ss.append(self.eat_sexp(depth+1))

            assert self.peek == ")"
            self.eat_char() # eat the closing brace
            print('*' * depth + f'{")"} @ {self.line}:{self.col}')

            rloc = self.loc
            return Sexp(ss, lloc, rloc)
        elif self.peek == '{':
            # keep stack of {'
            lloc = self.loc
            stack = [self.loc]
            self.eat_char() # eat '{'
            while stack:
                if self.eof:                                                        
                    raise RuntimeError(f"unclosed '}}' for code block at {stack[0]}. Closest '{{' is at {stack[-1]}")
                if self.peek == "{": stack.append(self.loc); self.eat_char()
                if self.peek == "}": stack.pop(); self.eat_char()
                else: self.eat_char()
            rloc = self.loc
            print(f"CodeBlock[{self.raw[lloc.ix:rloc.ix]}]")
            return CodeBlock(self.raw[lloc.ix:rloc.ix], lloc, rloc)
        elif Parser.is_atom_start(self.peek):
            # print(f'ATOM @ {self.line}:{self.col}')
            return self.eat_atom()
        else:
            raise RuntimeError(f"unknown character '{self.peek}' at {self.line}:{self.col}")

    def eat_sexps(self):
        sss = []
        while True:
            # eat crap till we get something interesting.
            while not self.eof and not self.peek == '(':
                self.eat_char()
            if self.eof: return sss

            # eat something interesting.
            sexp = self.eat_sexp(0)
            if not sexp: return sss
            sss.append(sexp)
            print("{:>10}/{:<10} {:<3}%".format(self.ix, len(self.raw), self.ix / len(self.raw) * 100))
  
class MatchProcessor:
    def __init__(self):
        self.raw = None
        with open("../raw_data/match.pd", "r") as f:
            self.raw = f.read()
        self.p = Parser(self.raw)
        self.sexps = self.p.eat_sexps()


m = MatchProcessor()
    
for sexp in m.sexps:
    print(sexp)

