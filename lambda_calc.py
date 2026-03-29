#!/usr/bin/env python3
"""lambda_calc - Lambda calculus interpreter with Church encodings."""
import sys, json

class Var:
    def __init__(self, name): self.name = name
    def __repr__(self): return self.name
    def __eq__(self, other): return isinstance(other, Var) and self.name == other.name

class Lam:
    def __init__(self, param, body): self.param = param; self.body = body
    def __repr__(self): return f"(λ{self.param}.{self.body})"

class App:
    def __init__(self, fn, arg): self.fn = fn; self.arg = arg
    def __repr__(self): return f"({self.fn} {self.arg})"

_counter = [0]
def fresh():
    _counter[0] += 1; return f"_v{_counter[0]}"

def subst(expr, name, val):
    if isinstance(expr, Var):
        return val if expr.name == name else expr
    if isinstance(expr, App):
        return App(subst(expr.fn, name, val), subst(expr.arg, name, val))
    if isinstance(expr, Lam):
        if expr.param == name: return expr
        if isinstance(val, Var) and val.name == expr.param:
            new_param = fresh()
            new_body = subst(expr.body, expr.param, Var(new_param))
            return Lam(new_param, subst(new_body, name, val))
        return Lam(expr.param, subst(expr.body, name, val))
    return expr

def beta_reduce(expr, max_steps=100):
    for _ in range(max_steps):
        reduced = _step(expr)
        if reduced is None: return expr
        expr = reduced
    return expr

def _step(expr):
    if isinstance(expr, App):
        if isinstance(expr.fn, Lam):
            return subst(expr.fn.body, expr.fn.param, expr.arg)
        fn_reduced = _step(expr.fn)
        if fn_reduced is not None: return App(fn_reduced, expr.arg)
        arg_reduced = _step(expr.arg)
        if arg_reduced is not None: return App(expr.fn, arg_reduced)
    if isinstance(expr, Lam):
        body_reduced = _step(expr.body)
        if body_reduced is not None: return Lam(expr.param, body_reduced)
    return None

# Church encodings
def church(n):
    body = Var("x")
    for _ in range(n): body = App(Var("f"), body)
    return Lam("f", Lam("x", body))

def unchurch(expr):
    expr = beta_reduce(expr)
    count = [0]
    fn = lambda: (count.__setitem__(0, count[0]+1), count[0])
    # Evaluate by applying to increment and 0
    result = beta_reduce(App(App(expr, Lam("n", App(Var("succ"), Var("n")))), Var("zero")))
    # Count applications
    n = 0; e = result
    while isinstance(e, App) and isinstance(e.fn, Var) and e.fn.name == "succ":
        n += 1; e = e.arg
    return n

SUCC = Lam("n", Lam("f", Lam("x", App(Var("f"), App(App(Var("n"), Var("f")), Var("x"))))))
PLUS = Lam("m", Lam("n", Lam("f", Lam("x", App(App(Var("m"), Var("f")), App(App(Var("n"), Var("f")), Var("x")))))))

def main():
    print("Lambda calculus demo\n")
    # Identity
    identity = Lam("x", Var("x"))
    result = beta_reduce(App(identity, Var("hello")))
    print(f"  (λx.x) hello = {result}")
    # Church numerals
    two = church(2); three = church(3)
    print(f"  Church 2 = {two}")
    print(f"  Church 3 = {three}")
    five = beta_reduce(App(App(PLUS, two), three))
    print(f"  2 + 3 = {five}")
    succ_two = beta_reduce(App(SUCC, two))
    print(f"  succ(2) = {succ_two}")
    # Boolean logic
    TRUE = Lam("t", Lam("f", Var("t")))
    FALSE = Lam("t", Lam("f", Var("f")))
    AND = Lam("p", Lam("q", App(App(Var("p"), Var("q")), Var("p"))))
    r = beta_reduce(App(App(AND, TRUE), FALSE))
    print(f"  TRUE AND FALSE = {r}")

if __name__ == "__main__":
    main()
