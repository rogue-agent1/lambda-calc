import argparse, re

def tokenize(s):
    return re.findall(r"[λ\\().a-z_][a-z0-9_]*|[λ\\().+*=]", s)

class Var:
    def __init__(self, name): self.name = name
    def __str__(self): return self.name

class Abs:
    def __init__(self, param, body): self.param, self.body = param, body
    def __str__(self): return f"(λ{self.param}.{self.body})"

class App:
    def __init__(self, func, arg): self.func, self.arg = func, arg
    def __str__(self): return f"({self.func} {self.arg})"

def parse(tokens):
    def parse_expr():
        terms = []
        while tokens and tokens[0] not in (")", ""):
            if tokens[0] in ("λ", "\\"):
                tokens.pop(0)
                param = tokens.pop(0)
                if tokens and tokens[0] == ".": tokens.pop(0)
                body = parse_expr()
                terms.append(Abs(param, body))
            elif tokens[0] == "(":
                tokens.pop(0)
                terms.append(parse_expr())
                if tokens and tokens[0] == ")": tokens.pop(0)
            else:
                terms.append(Var(tokens.pop(0)))
        result = terms[0] if terms else Var("_")
        for t in terms[1:]: result = App(result, t)
        return result
    return parse_expr()

def substitute(expr, name, val):
    if isinstance(expr, Var): return val if expr.name == name else expr
    if isinstance(expr, Abs):
        if expr.param == name: return expr
        return Abs(expr.param, substitute(expr.body, name, val))
    if isinstance(expr, App):
        return App(substitute(expr.func, name, val), substitute(expr.arg, name, val))

def reduce(expr, limit=100):
    for _ in range(limit):
        if isinstance(expr, App) and isinstance(expr.func, Abs):
            expr = substitute(expr.func.body, expr.func.param, expr.arg)
        elif isinstance(expr, App):
            expr = App(reduce(expr.func, limit//2), reduce(expr.arg, limit//2))
            break
        else: break
    return expr

def main():
    p = argparse.ArgumentParser(description="Lambda calculus")
    p.add_argument("expr", nargs="+")
    p.add_argument("--steps", type=int, default=100)
    args = p.parse_args()
    text = " ".join(args.expr)
    tokens = tokenize(text)
    expr = parse(tokens)
    print(f"Parsed:  {expr}")
    result = reduce(expr, args.steps)
    print(f"Reduced: {result}")

if __name__ == "__main__":
    main()
