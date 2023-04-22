### BNF for arithmetic expressions
# Source: https://en.wikipedia.org/wiki/Syntax_diagram#Example

"""
<expression> ::= <term> | <term> "+" <expression>
<term>       ::= <factor> | <factor> "*" <term>
<factor>     ::= <constant> | <variable> | "(" <expression> ")"
<variable>   ::= "x" | "y" | "z"
<constant>   ::= <digit> | <digit> <constant>
<digit>      ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
"""


### BNF in JSON-like format

bnf_syntax = {
    "expression": [["term", "sumop", "expression"], ["term"]],
    "sumop": [["+"], ["-"]],
    "term": [["factor", "prodop", "term"], ["factor"]],
    "prodop": [["*"], ["/"]],
    "factor": [["constant"], ["variable"], ["(", "expression", ")"]],
    "variable": [["x"], ["y"], ["z"]],
    "constant": [["digit", "constant"], ["digit"]],
    "digit": [["0"], ["1"], ["2"], ["3"], ["4"], ["5"], ["6"], ["7"], ["8"], ["9"]],
}


### Tokenizer

# This section is left blank: 1 string character = 1 token


### Parser

ParseError = (ValueError, IndexError)


def parse_part(tokens, j, part, syntax):
    if part in syntax:
        return parse(tokens, j, part, syntax)
    elif part == tokens[j]:  # terminal token
        return j+1, tokens[j]
    else:
        raise ValueError


def parse_rule(tokens, i, rule, syntax):
    parts = []
    for part in rule:
        i, el = parse_part(tokens, i, part, syntax)
        parts.append(el)
    return i, parts


def parse(tokens, i, identifier, syntax):
    for rule in syntax[identifier]:
        try:
            i, parts = parse_rule(tokens, i, rule, syntax)
            return i, (identifier, parts)
        except ParseError:
            pass
    raise ValueError


def parse_expression(expression):
    return parse(expression, 0, "expression", bnf_syntax)[1]


### Evaluator

import operator


def numjoin(a, b):
    """numjoin(12, 34) == 1234"""
    return int(str(a) + str(b))


def evaluate(tree):
    # The matching logic of this function matches the syntax tree closely,
    # but defines behavior to the parts.
    identifier, parts = tree

    if identifier == "expression":
        if len(parts) == 1:
            return evaluate(parts[0])
        elif len(parts) == 3:
            binop = evaluate(parts[1])
            return binop(evaluate(parts[0]), evaluate(parts[2]))
        else:
            raise TypeError

    elif identifier == "sumop":
        if len(parts) == 1 and parts[0] == "+":
            return operator.add
        elif len(parts) == 1 and parts[0] == "-":
            return operator.sub
        else:
            raise TypeError

    elif identifier == "term":
        # same pattern here as for "expression"
        if len(parts) == 1:
            return evaluate(parts[0])
        elif len(parts) == 3:
            binop = evaluate(parts[1])
            return binop(evaluate(parts[0]), evaluate(parts[2]))
        else:
            raise TypeError

    elif identifier == "prodop":
        if len(parts) == 1 and parts[0] == "*":
            return operator.mul
        elif len(parts) == 1 and parts[0] == "/":
            return operator.truediv
        else:
            raise TypeError

    elif identifier == "factor":
        if len(parts) == 1 and parts[0][0] == "constant":
            return evaluate(parts[0])
        elif len(parts) == 1 and parts[0][0] == "variable":
            return evaluate(parts[0])
        elif len(parts) == 3 and parts[1][0] == "expression":
            return evaluate(parts[1])
        else:
            raise TypeError

    elif identifier == "variable":
        if len(parts) == 1 and parts[0] == "x":
            return x
        elif len(parts) == 1 and parts[0] == "y":
            return y
        elif len(parts) == 1 and parts[0] == "z":
            return z
        else:
            raise TypeError

    elif identifier == "constant":
        if len(parts) == 1:
            return evaluate(parts[0])
        elif len(parts) == 2:
            return numjoin(evaluate(parts[0]), evaluate(parts[1]))
        else:
            raise TypeError

    elif identifier == "digit":
        if len(parts) == 1:
            return int(parts[0])
        else:
            raise TypeError

    else:
        raise TypeError(f"Unknown identifier {identifier}")


### Main program

if __name__ == "__main__":
    from pprint import pp as print

    expression = "10+2*x+3*(y+z)/2"

    tree = parse_expression(expression)
    print(tree)

    (x, y, z) = (1, 2, 3)
    value = evaluate(tree)
    print(value)

    (x, y, z) = (10, 2, 4)
    value = evaluate(tree)
    print(value)

    ## Note:
    # We could also pass (x, y, z) down as a parameter to evaluate the
    # expression, with some modification to the `evaluate` function. That would
    # be preferable, since we generally don't want functions to be using
    # nonlocal variables. We also don't want to mutate variable to call a
    # function. This would however mean that we pass it as an argument in all
    # the recursive function calls, and would make the code slightly harder to
    # read.

    ## Note:
    # Two other concepts are also useful:
    # * Expression printer: (tree) -> (source text)
    #     Turn the expression tree back into source text.
    #     This is common for pretty printing or code minifiers.
    # * Expression generator: (syntax) -> (random tree) -> (random source text)
    #     Generate random syntactically valid sentences
    #     using the syntax diagram to randomly select tokens.

    ## Note:
    # Tokenizers and lexers can also be useful to group symbols.
    # E.g.: A tokenizer could turn 123 into a single number instead of three
    # digits.
