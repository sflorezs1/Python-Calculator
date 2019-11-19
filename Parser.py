from math import sin, cos, tan, sinh, log, cosh, radians


class ParseError(Exception):
    pass


class UnevenParenthesisException(Exception):
    pass


class UnimplementedTermException(Exception):
    pass


class UnrecognizedLogicOperatorException(Exception):
    pass


class IncompleteLoopException(Exception):
    pass


class IncompleteTernaryException(Exception):
    pass


def is_numeric(expression: str):
    try:
        float(expression)
        return True
    except ValueError:
        return False


def is_operator(token: str):
    return token in "+*/^%?:;()[]"


def find_op(expression: str):
    if expression.find("<=") != -1:
        return "<="
    elif expression.find("==") != -1:
        return "=="
    elif expression.find(">=") != -1:
        return ">="
    elif expression.find(">") != -1:
        return ">"
    elif expression.find("<") != -1:
        return "<"
    else:
        raise IncompleteTernaryException("Logic operator was not given at expression {%s}" % expression)


def do_logic(a: float, b: float, logic_op: str):
    if logic_op == "<":
        return a < b
    elif logic_op == ">":
        return a > b
    elif logic_op == "<=":
        return a <= b
    elif logic_op == ">=":
        return a >= b
    elif logic_op == "==":
        return a == b
    else:
        raise UnrecognizedLogicOperatorException("Operator: %s" % logic_op)


def is_condition(expression: str):
    booleans: [str] = ['<=', '>=', '<', '>']
    for i in booleans:
        if i in expression:
            return i
    return False


class Parser(object):

    def __init__(self, expression: str):
        self.expression: str = expression.strip().replace(" ", "").replace("--", "+")

    def parse(self, expression: str = None):
        if expression is None:
            expression = self.expression
        if expression.count(";") % 3 != 0:
            raise IncompleteLoopException("Please check the expression,"
                                          " the loop at {%s} may be incomplete" % expression)
        if "?" in expression and ":" not in expression:
            raise IncompleteTernaryException("Please check the expression, "
                                             "the conditional at {%s} may be incomplete" % expression)
        if "(" in expression or ")" in expression:
            return self._parse_grouping(expression, ("(", ")"))
        elif "[" in expression or "]" in expression:
            return self._parse_grouping(expression, ("[", "]"))
        elif "?" in expression:
            return self._parse_if(expression)
        elif ";" in expression:
            return self._parse_loop(expression)
        elif "*-" in expression:
            return self._parse_op_neg(expression, "*-")
        elif "/-" in expression:
            return self._parse_op_neg(expression, "/-")
        elif "%-" in expression:
            return self._parse_op_neg(expression, "%-")
        elif "+" in expression:
            return self._parse_basic(expression, "+", 0, lambda a, b: a + b)
        elif "-" in expression:
            return self._parse_basic(expression, "-", 0, lambda a, b: a - b)
        elif "*" in expression:
            return self._parse_basic(expression, "*", 1, lambda a, b: a * b)
        elif "/" in expression:
            return self._parse_basic(expression, "/", 1, lambda a, b: a / b)
        elif "%" in expression:
            return self._parse_basic(expression, "%", 1, lambda a, b: a % b)
        elif "^" in expression:
            return self._parse_basic(expression, "^", 1, lambda a, b: a ** b)
        elif "Sinh" in expression:
            return self._parse_math_func(expression, "Sinh", lambda a: sinh(radians(a)))
        elif "Cosh" in expression:
            return self._parse_math_func(expression, "Cosh", lambda a: cosh(radians(a)))
        elif "Sin" in expression:
            return self._parse_math_func(expression, "Sin", lambda a: sin(radians(a)))
        elif "Cos" in expression:
            return self._parse_math_func(expression, "Cos", lambda a: cos(radians(a)))
        elif "Tan" in expression:
            return self._parse_math_func(expression, "Tan", lambda a: tan(radians(a)))
        elif "Ln" in expression:
            return self._parse_math_func(expression, "Ln", log)
        elif is_numeric(expression):
            return float(expression)
        else:
            raise UnimplementedTermException("Unimplemented operation at expression %s" % expression)

    def _parse_grouping(self, expression: str, groupers: (str, str)):
        if expression.count(groupers[0]) != expression.count(groupers[1]):
            raise UnevenParenthesisException("The number of brackets in expression {%s}"
                                             " are uneven, please check your expression." % expression)
        count_open = count_close = idx_open = idx_close = 0
        for i, x in enumerate(expression):
            if x == groupers[0]:
                if count_open == 0:
                    idx_open = i
                count_open += 1
            elif x == groupers[1]:
                count_close += 1
            if count_open == count_close and count_open > 0:
                idx_close = i
                break
        return self.parse(expression[0:idx_open] + str(self.parse(expression[idx_open + 1: idx_close])) +
                          expression[idx_close + 1:])

    def _parse_if(self, expression: str):
        logic_op: str = find_op(expression)
        idx_q: int = expression.find("?")
        idx_lop: int = expression.find(logic_op)
        idx_opt: int = expression.find(":")
        left: float = self.parse(expression[:idx_lop])
        right: float = self.parse(expression[idx_lop + len(logic_op):idx_q])
        if do_logic(left, right, logic_op):
            return self.parse(expression[idx_q + 1:idx_opt])
        else:
            return self.parse(expression[idx_opt + 1:])

    def _parse_loop(self, expression: str):
        a: int = expression.find(";")
        b: int = expression[a + 1:].find(";") + a + 1
        c: int = expression[b + 1:].find(";") + b + 1
        initial: float = self.parse(expression[:a])
        final: float = self.parse(expression[a + 2: b])
        variation: float = self.parse(expression[b + 1: c])
        expr: float = self.parse(expression[c + 1:])
        result = 0
        which: str = find_op(expression)
        while do_logic(initial, final, which):
            result += expr
            initial += variation
        return result

    def _parse_basic(self, expression: str, op_s: str, base_case: float, f):
        expressions: [str] = expression.split(op_s)
        result = base_case if expressions[0] == '' or is_operator(expressions[0][-1]) else self.parse(expressions[0])
        for i in range(1, len(expressions)):
            if expressions[i] != '':
                result = f(result, self.parse(expressions[i]))
        return result

    def _parse_op_neg(self, expression: str, operator: str):
        where: int = expression.find(operator)
        a: int = 0
        b: int = len(expression)
        for i in range(1, len(expression) - where):
            if a == 0:
                if where - i > 0:
                    if is_operator(expression[where - i]):
                        a = where - i
            if b == len(expression):
                if is_operator(expression[where + i]):
                    b = where + i
        num_1 = self.parse(expression[a:where])
        num_2 = self.parse(expression[where+1:b])
        expression = expression[0:a] + str(num_1 * num_2) + expression[b:]
        return self.parse(expression)

    def _parse_math_func(self, expression: str, op_s: str, f):
        return f(self.parse(expression[expression.find(op_s) + len(op_s):]))


if __name__ == '__main__':
    def main():
        result = SyntaxError("Syntax Error")
        try:
            result = Parser(input("Expression: ")).parse()
        except ParseError:
            print("An error occurred while parsing")
        except UnevenParenthesisException as e:
            print(str(e.args[0]))
        except UnimplementedTermException as ex:
            print(str(ex.args[0]))
        except IncompleteTernaryException as e:
            print(str(e.args[0]))
        except IncompleteLoopException as ex:
            print(str(ex.args[0]))
        finally:
            if isinstance(result, SyntaxError):
                print(result)
            else:
                print("result: %.2f" % result)
    main()
