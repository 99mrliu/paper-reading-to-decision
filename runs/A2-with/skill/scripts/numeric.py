"""Finite, sign-preserving numeric evidence helpers; no scientific certification."""
import ast
from decimal import Decimal, InvalidOperation
import math
import re
import unicodedata

PAT = re.compile(r'(?<![\w.])[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?')


def normalize(s):
    s = unicodedata.normalize('NFC', str(s)).replace('−', '-').replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    s = re.sub(r'(?<=\d)[–—-](?=\d)', ' ', s)
    s = s.replace('–', '-').replace('—', '-')
    s = re.sub(r'-\s*\n\s*', '', s)
    return re.sub(r'\s+', ' ', s).strip()


def finite(x):
    if isinstance(x, bool):
        raise ValueError('boolean is not numeric evidence')
    y = float(x)
    if not math.isfinite(y):
        raise ValueError('number must be finite')
    return y


def numbers(text):
    text = normalize(text)
    text = re.sub(r'(?<=\d),(?=\d{3}(?:\D|$))', '', text)
    return [Decimal(x) for x in PAT.findall(text)]


def contains(value, observed):
    finite(value)
    return Decimal(str(value)) in observed


FUNCS = {'max': max, 'min': min, 'abs': abs, 'round': round, 'sqrt': math.sqrt}
OPS = {ast.Add: lambda a,b:a+b, ast.Sub:lambda a,b:a-b, ast.Mult:lambda a,b:a*b,
       ast.Div:lambda a,b:a/b, ast.Mod:lambda a,b:a%b}


def evaluate(formula, inputs):
    env = {k: finite(v) for k,v in inputs.items()}
    tree = ast.parse(formula, mode='eval')
    if len(list(ast.walk(tree))) > 80:
        raise ValueError('formula too large')
    def visit(n):
        if isinstance(n, ast.Constant): return finite(n.value)
        if isinstance(n, ast.Name): return env[n.id]
        if isinstance(n, ast.UnaryOp) and isinstance(n.op,(ast.USub,ast.UAdd)):
            return finite((-1 if isinstance(n.op,ast.USub) else 1)*visit(n.operand))
        if isinstance(n, ast.BinOp):
            a,b=visit(n.left),visit(n.right)
            if isinstance(n.op,ast.Pow):
                if abs(b)>100 or abs(a)>1e100: raise ValueError('power out of bounds')
                return finite(a**b)
            if type(n.op) in OPS:return finite(OPS[type(n.op)](a,b))
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in FUNCS and not n.keywords:
            args=[visit(x) for x in n.args]
            if n.func.id=='round' and len(args)==2:args[1]=int(args[1])
            return finite(FUNCS[n.func.id](*args))
        raise ValueError('unsupported formula syntax')
    return visit(tree.body)
