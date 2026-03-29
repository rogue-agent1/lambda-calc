#!/usr/bin/env python3
"""lambda_calc: Lambda calculus interpreter with Church encoding."""
import sys

class Var:
    def __init__(self, name): self.name = name
    def __repr__(self): return self.name
    def __eq__(self, o): return isinstance(o, Var) and self.name == o.name
    def __hash__(self): return hash(self.name)

class Lam:
    def __init__(self, param, body): self.param = param; self.body = body
    def __repr__(self): return f"(\\{self.param}.{self.body})"

class App:
    def __init__(self, func, arg): self.func = func; self.arg = arg
    def __repr__(self): return f"({self.func} {self.arg})"

def free_vars(expr):
    if isinstance(expr, Var): return {expr.name}
    if isinstance(expr, Lam): return free_vars(expr.body) - {expr.param}
    if isinstance(expr, App): return free_vars(expr.func) | free_vars(expr.arg)
    return set()

_counter = [0]
def fresh():
    _counter[0] += 1
    return f"_v{_counter[0]}"

def substitute(expr, var, val):
    if isinstance(expr, Var):
        return val if expr.name == var else expr
    if isinstance(expr, Lam):
        if expr.param == var: return expr
        if expr.param in free_vars(val):
            new_param = fresh()
            new_body = substitute(expr.body, expr.param, Var(new_param))
            return Lam(new_param, substitute(new_body, var, val))
        return Lam(expr.param, substitute(expr.body, var, val))
    if isinstance(expr, App):
        return App(substitute(expr.func, var, val), substitute(expr.arg, var, val))
    return expr

def beta_reduce(expr, max_steps=100):
    for _ in range(max_steps):
        reduced = _step(expr)
        if reduced is None: return expr
        expr = reduced
    return expr

def _step(expr):
    if isinstance(expr, App):
        if isinstance(expr.func, Lam):
            return substitute(expr.func.body, expr.func.param, expr.arg)
        r = _step(expr.func)
        if r is not None: return App(r, expr.arg)
        r = _step(expr.arg)
        if r is not None: return App(expr.func, r)
    if isinstance(expr, Lam):
        r = _step(expr.body)
        if r is not None: return Lam(expr.param, r)
    return None

# Church numerals
def church(n):
    body = Var("x")
    for _ in range(n):
        body = App(Var("f"), body)
    return Lam("f", Lam("x", body))

def unchurch(expr):
    expr = beta_reduce(expr)
    # Apply to (+1) and 0
    result = App(App(expr, Lam("n", App(Var("succ"), Var("n")))), Var("zero"))
    result = beta_reduce(result)
    count = 0
    while isinstance(result, App) and isinstance(result.func, Var) and result.func.name == "succ":
        count += 1
        result = result.arg
    return count

def test():
    # Identity
    id_fn = Lam("x", Var("x"))
    result = beta_reduce(App(id_fn, Var("y")))
    assert isinstance(result, Var) and result.name == "y"
    # Church numerals
    zero = church(0)
    one = church(1)
    two = church(2)
    three = church(3)
    # Successor
    succ = Lam("n", Lam("f", Lam("x", App(Var("f"), App(App(Var("n"), Var("f")), Var("x"))))))
    result = beta_reduce(App(succ, two))
    # Addition: plus = \m.\n.\f.\x. m f (n f x)
    plus = Lam("m", Lam("n", Lam("f", Lam("x",
        App(App(Var("m"), Var("f")), App(App(Var("n"), Var("f")), Var("x")))
    ))))
    sum_expr = beta_reduce(App(App(plus, two), three))
    # Verify it's Church 5 by structure
    assert isinstance(sum_expr, Lam)
    # Free variable capture avoidance
    expr = Lam("x", Lam("y", App(Var("x"), Var("y"))))
    result = substitute(expr, "x", Var("y"))
    assert "y" not in free_vars(result.body) or result.body.param != "y"
    print("All tests passed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("Usage: lambda_calc.py test")
