"""
Interpreter for Bangla Programming Language
==============================================
Kaj: Parser-er AST tree "walk" kore actual execution kora — variable e
value rakha, condition check kora, loop chalano, function call kora,
ar screen-e output dekhano.

Eita "Tree-Walking Interpreter" pattern use kore: প্রতিটা node type-এর
জন্য একটা _exec_* / _eval_* method ache, jeta সেই node-টার কাজ actually করে।
"""

import math
import sys
import unicodedata

try:
    from .ast_nodes import (
        NumberNode, StringNode, BooleanNode, NullNode, ListNode, IdentifierNode,
        BinaryOpNode, UnaryOpNode, CallNode, IndexNode, IndexAssignNode,
        VarDeclNode, AssignNode, PrintNode, IfNode, WhileNode, ForNode,
        FunctionDefNode, ReturnNode, BreakNode, ContinueNode,
        ExpressionStatementNode, ProgramNode,
    )
except ImportError:
    from ast_nodes import (
        NumberNode, StringNode, BooleanNode, NullNode, ListNode, IdentifierNode,
        BinaryOpNode, UnaryOpNode, CallNode, IndexNode, IndexAssignNode,
        VarDeclNode, AssignNode, PrintNode, IfNode, WhileNode, ForNode,
        FunctionDefNode, ReturnNode, BreakNode, ContinueNode,
        ExpressionStatementNode, ProgramNode,
    )


# Map Banglish and native Bangla built-in names to canonical built-in handlers.
_RAW_BUILTIN_ALIASES = {
    # I/O
    "nao": "nao",
    "নাও": "nao",
    # List / String operations
    "dhoirgo": "dhoirgo",
    "দৈর্ঘ্য": "dhoirgo",
    "juktokoro": "juktokoro",
    "যুক্তকরো": "juktokoro",
    "যুক্ত_করো": "juktokoro",
    "bad_dao": "bad_dao",
    "বাদ_দাও": "bad_dao",
    "বাদদাও": "bad_dao",
    "shajao": "shajao",
    "সাজাও": "shajao",
    "ulto": "ulto",
    "উল্টো": "ulto",
    "jog_koro": "jog_koro",
    "যোগ_করো": "jog_koro",
    "যোগকরো": "jog_koro",
    "shorbo_boro": "shorbo_boro",
    "সর্বোচ্চ": "shorbo_boro",
    "সর্ববড়": "shorbo_boro",
    "সর্ব_বড়": "shorbo_boro",
    "shorbo_choto": "shorbo_choto",
    "সর্বনিম্ন": "shorbo_choto",
    "সর্বছোট": "shorbo_choto",
    "সর্ব_ছোট": "shorbo_choto",
    "ache": "ache",
    "আছে": "ache",
    "porishor": "porishor",
    "পরিসর": "porishor",
    "boro_hater": "boro_hater",
    "বড়_হাতের": "boro_hater",
    "choto_hater": "choto_hater",
    "ছোট_হাতের": "choto_hater",
    "bhangao": "bhangao",
    "ভাঙো": "bhangao",
    "ভাঙ্গো": "bhangao",
    # Type conversion & inspection
    "purno": "purno",
    "পূর্ণ": "purno",
    "doshomik": "doshomik",
    "দশমিক": "doshomik",
    "lekha": "lekha",
    "লেখা": "lekha",
    "dhoron": "dhoron",
    "ধরন": "dhoron",
    # Math
    "porom": "porom",
    "পরম": "porom",
    "borgomul": "borgomul",
    "বর্গমূল": "borgomul",
    "ghat": "ghat",
    "ঘাত": "ghat",
}

BUILTIN_ALIASES = {unicodedata.normalize("NFC", k): v for k, v in _RAW_BUILTIN_ALIASES.items()}


# ---------------------------------------------------------
# Runtime errors & control-flow signals
# ---------------------------------------------------------
class BanglaRuntimeError(Exception):
    """Actual error dekhano user-ke, jemon: variable na thakle, type mismatch hole."""
    pass


class BreakSignal(Exception):
    """thamo / থামো (break) hole ei signal internally throw hoy."""
    pass


class ContinueSignal(Exception):
    """cholo / চলো (continue) hole ei signal throw hoy."""
    pass


class ReturnSignal(Exception):
    """ferot / ফেরত (return) hole ei signal throw hoy."""
    def __init__(self, value):
        self.value = value


# ---------------------------------------------------------
# Environment — variable/function storage (scope handle kore)
# ---------------------------------------------------------
class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def define(self, name, value):
        """notun variable banano ei scope-e"""
        self.vars[name] = value

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise BanglaRuntimeError(f"'{name}' নামে কোনো variable পাওয়া যায়নি (undefined variable)")

    def set(self, name, value):
        """already existing variable-e notun value bosano (nearest scope khuje)"""
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent is not None:
            self.parent.set(name, value)
            return
        raise BanglaRuntimeError(f"'{name}' নামে কোনো variable পাওয়া যায়নি (undefined variable)")


# ---------------------------------------------------------
# Function object — user-defined function represent kore
# ---------------------------------------------------------
class BanglaFunction:
    def __init__(self, name, params, body, closure_env):
        self.name = name
        self.params = params
        self.body = body
        self.closure_env = closure_env

    def __repr__(self):
        return f"<function {self.name}>"


# ---------------------------------------------------------
# Interpreter
# ---------------------------------------------------------
class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self._builtin_handlers = {
            "nao": self._builtin_nao,
            "dhoirgo": self._builtin_dhoirgo,
            "juktokoro": self._builtin_juktokoro,
            "bad_dao": self._builtin_bad_dao,
            "shajao": self._builtin_shajao,
            "ulto": self._builtin_ulto,
            "jog_koro": self._builtin_jog_koro,
            "shorbo_boro": lambda n, e: self._list_extremum(n, e, find_max=True),
            "shorbo_choto": lambda n, e: self._list_extremum(n, e, find_max=False),
            "ache": self._builtin_ache,
            "porishor": self._builtin_porishor,
            "boro_hater": lambda n, e: self._transform_str(n, e, str.upper),
            "choto_hater": lambda n, e: self._transform_str(n, e, str.lower),
            "bhangao": self._builtin_bhangao,
            "purno": self._builtin_purno,
            "doshomik": self._builtin_doshomik,
            "lekha": self._builtin_lekha,
            "dhoron": self._builtin_dhoron,
            "porom": self._builtin_porom,
            "borgomul": self._builtin_borgomul,
            "ghat": self._builtin_ghat,
        }

    # ---- entry point -----------------------------------------------
    def interpret(self, program_node):
        self._execute_block(program_node.statements, self.global_env)

    # ---- statement execution -----------------------------------------
    def _execute_block(self, statements, env):
        result = None
        for stmt in statements:
            result = self._execute(stmt, env)
        return result

    def _execute(self, node, env):
        method_name = f"_exec_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise BanglaRuntimeError(f"Unknown statement type: {type(node).__name__}")
        return method(node, env)

    def _exec_VarDeclNode(self, node, env):
        value = self._evaluate(node.value_expr, env)
        env.define(node.name, value)

    def _exec_AssignNode(self, node, env):
        value = self._evaluate(node.value_expr, env)
        env.set(node.name, value)

    def _exec_PrintNode(self, node, env):
        value = self._evaluate(node.expr, env)
        print(self._to_display_string(value))

    def _exec_IfNode(self, node, env):
        condition = self._evaluate(node.condition, env)
        if self._is_truthy(condition):
            self._execute_block(node.then_branch, Environment(env))
        elif node.else_branch is not None:
            self._execute_block(node.else_branch, Environment(env))

    def _exec_WhileNode(self, node, env):
        while self._is_truthy(self._evaluate(node.condition, env)):
            try:
                self._execute_block(node.body, Environment(env))
            except BreakSignal:
                break
            except ContinueSignal:
                continue

    def _exec_ForNode(self, node, env):
        loop_env = Environment(env)
        self._execute(node.init, loop_env)
        while self._is_truthy(self._evaluate(node.condition, loop_env)):
            try:
                self._execute_block(node.body, Environment(loop_env))
            except BreakSignal:
                break
            except ContinueSignal:
                pass
            self._execute(node.update, loop_env)

    def _exec_FunctionDefNode(self, node, env):
        func = BanglaFunction(node.name, node.params, node.body, env)
        env.define(node.name, func)

    def _exec_ReturnNode(self, node, env):
        value = self._evaluate(node.expr, env) if node.expr is not None else None
        raise ReturnSignal(value)

    def _exec_BreakNode(self, node, env):
        raise BreakSignal()

    def _exec_ContinueNode(self, node, env):
        raise ContinueSignal()

    def _exec_IndexAssignNode(self, node, env):
        collection = self._evaluate(node.collection, env)
        index = self._evaluate(node.index_expr, env)
        if not isinstance(collection, list):
            raise BanglaRuntimeError(f"Index দিয়ে value বসানো শুধু array/talika-তে করা যায়, পাওয়া গেছে: {collection!r}")
        self._check_index(collection, index)
        collection[int(index)] = self._evaluate(node.value_expr, env)

    def _exec_ExpressionStatementNode(self, node, env):
        return self._evaluate(node.expr, env)

    # ---- expression evaluation ------------------------------------------
    def _evaluate(self, node, env):
        method_name = f"_eval_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise BanglaRuntimeError(f"Unknown expression type: {type(node).__name__}")
        return method(node, env)

    def _eval_NumberNode(self, node, env):
        return node.value

    def _eval_StringNode(self, node, env):
        return node.value

    def _eval_BooleanNode(self, node, env):
        return node.value

    def _eval_NullNode(self, node, env):
        return None

    def _eval_ListNode(self, node, env):
        return [self._evaluate(e, env) for e in node.elements]

    def _eval_IdentifierNode(self, node, env):
        return env.get(node.name)

    def _eval_IndexNode(self, node, env):
        collection = self._evaluate(node.collection, env)
        index = self._evaluate(node.index_expr, env)
        if isinstance(collection, (str, list)):
            self._check_index(collection, index)
            return collection[int(index)]
        raise BanglaRuntimeError(f"Index (nums[i]) শুধু array/talika বা string-এ করা যায়, পাওয়া গেছে: {collection!r}")

    @staticmethod
    def _check_index(collection, index):
        if not isinstance(index, (int, float)) or isinstance(index, bool):
            raise BanglaRuntimeError(f"Index অবশ্যই একটা সংখ্যা হতে হবে, পাওয়া গেছে: {index!r}")
        idx = int(index)
        if idx < 0 or idx >= len(collection):
            raise BanglaRuntimeError(
                f"Index {idx} এর বাইরে (out of range) — সাইজ {len(collection)}"
            )

    def _eval_UnaryOpNode(self, node, env):
        val = self._evaluate(node.operand, env)
        if node.operator == "MINUS":
            self._check_number(val, "unary -")
            return -val
        if node.operator == "NOT":
            return not self._is_truthy(val)
        raise BanglaRuntimeError(f"Unknown unary operator: {node.operator}")

    def _eval_BinaryOpNode(self, node, env):
        op = node.operator

        # short-circuit logical operators
        if op == "AND":
            left = self._evaluate(node.left, env)
            return self._is_truthy(self._evaluate(node.right, env)) if self._is_truthy(left) else False
        if op == "OR":
            left = self._evaluate(node.left, env)
            return True if self._is_truthy(left) else self._is_truthy(self._evaluate(node.right, env))

        left = self._evaluate(node.left, env)
        right = self._evaluate(node.right, env)

        if op == "PLUS":
            if isinstance(left, str) or isinstance(right, str):
                return self._to_display_string(left) + self._to_display_string(right)
            if isinstance(left, list) and isinstance(right, list):
                return left + right
            self._check_number(left, "+"); self._check_number(right, "+")
            return left + right

        numeric_ops = {
            "MINUS": ("-", lambda a, b: a - b),
            "STAR": ("*", lambda a, b: a * b),
            "POWER": ("**", lambda a, b: a ** b),
        }
        if op in numeric_ops:
            symbol, fn = numeric_ops[op]
            self._check_number(left, symbol); self._check_number(right, symbol)
            return fn(left, right)

        if op in ("SLASH", "PERCENT"):
            symbol = "/" if op == "SLASH" else "%"
            self._check_number(left, symbol); self._check_number(right, symbol)
            if right == 0:
                raise BanglaRuntimeError("শূন্য দিয়ে ভাগ করা যায় না (division by zero)")
            return left / right if op == "SLASH" else left % right

        if op == "EQ":
            return left == right
        if op == "NEQ":
            return left != right

        cmp_ops = {
            "GT": lambda a, b: a > b,
            "LT": lambda a, b: a < b,
            "GTE": lambda a, b: a >= b,
            "LTE": lambda a, b: a <= b,
        }
        if op in cmp_ops:
            try:
                return cmp_ops[op](left, right)
            except TypeError:
                raise BanglaRuntimeError(f"'{op}' দিয়ে {left!r} এবং {right!r} তুলনা করা যায় না")

        raise BanglaRuntimeError(f"Unknown binary operator: {op}")

    def _eval_CallNode(self, node, env):
        canonical = BUILTIN_ALIASES.get(node.callee_name)
        if canonical is not None:
            handler = self._builtin_handlers[canonical]
            return handler(node, env)

        func = env.get(node.callee_name)
        if not isinstance(func, BanglaFunction):
            raise BanglaRuntimeError(f"'{node.callee_name}' একটা function না, call করা যাবে না")

        if len(node.arguments) != len(func.params):
            raise BanglaRuntimeError(
                f"'{func.name}' function-এর {len(func.params)} টা argument দরকার, "
                f"কিন্তু {len(node.arguments)} টা দেওয়া হয়েছে"
            )

        call_env = Environment(func.closure_env)
        for param_name, arg_node in zip(func.params, node.arguments):
            call_env.define(param_name, self._evaluate(arg_node, env))

        try:
            self._execute_block(func.body, call_env)
        except ReturnSignal as ret:
            return ret.value

        return None

    # ---- built-in implementations ------------------------------------
    def _eval_args(self, node, env, min_args, max_args=None):
        """Validate argument count and evaluate all arguments left-to-right."""
        max_args = min_args if max_args is None else max_args
        count = len(node.arguments)
        if count < min_args or count > max_args:
            expected = f"{min_args}" if min_args == max_args else f"{min_args} থেকে {max_args}"
            raise BanglaRuntimeError(
                f"'{node.callee_name}' এর {expected} টা argument দরকার, "
                f"কিন্তু {count} টা দেওয়া হয়েছে"
            )
        return [self._evaluate(arg, env) for arg in node.arguments]

    def _builtin_nao(self, node, env):
        args = self._eval_args(node, env, 0, 1)
        prompt = self._to_display_string(args[0]) if args else ""
        try:
            if not sys.stdin.isatty():
                if prompt:
                    sys.stdout.write(prompt)
                sys.stdout.flush()
                line = sys.stdin.readline()
                if line == "":
                    raise EOFError()
                return line.rstrip("\r\n")
            return input(prompt)
        except EOFError:
            raise BanglaRuntimeError("ইনপুট নেওয়া সম্ভব হয়নি (ইনপুট স্ট্রিম বন্ধ হয়েছে)")

    def _builtin_dhoirgo(self, node, env):
        val = self._eval_args(node, env, 1)[0]
        if isinstance(val, (list, str)):
            return len(val)
        raise BanglaRuntimeError(f"'{node.callee_name}' শুধু array/talika বা string-এ কাজ করে, পাওয়া গেছে: {val!r}")

    def _builtin_juktokoro(self, node, env):
        lst, value = self._eval_args(node, env, 2)
        if not isinstance(lst, list):
            raise BanglaRuntimeError(f"'{node.callee_name}' শুধু array/talika-তে কাজ করে, পাওয়া গেছে: {lst!r}")
        lst.append(value)
        return lst

    def _builtin_bad_dao(self, node, env):
        args = self._eval_args(node, env, 1, 2)
        lst = args[0]
        if not isinstance(lst, list):
            raise BanglaRuntimeError(f"'{node.callee_name}' শুধু array/talika-তে কাজ করে, পাওয়া গেছে: {lst!r}")
        if not lst:
            raise BanglaRuntimeError(f"'{node.callee_name}' এর জন্য তালিকা খালি রাখা যাবে না")
        if len(args) == 1:
            return lst.pop()
        self._check_index(lst, args[1])
        return lst.pop(int(args[1]))

    def _builtin_shajao(self, node, env):
        lst = self._eval_args(node, env, 1)[0]
        if not isinstance(lst, list):
            raise BanglaRuntimeError(f"'{node.callee_name}' শুধু array/talika-তে কাজ করে, পাওয়া গেছে: {lst!r}")
        try:
            return sorted(lst)
        except TypeError:
            raise BanglaRuntimeError(f"'{node.callee_name}' এর জন্য array-এর সব element একই ধরনের হতে হবে")

    def _builtin_ulto(self, node, env):
        val = self._eval_args(node, env, 1)[0]
        if isinstance(val, list):
            return list(reversed(val))
        if isinstance(val, str):
            return val[::-1]
        raise BanglaRuntimeError(f"'{node.callee_name}' শুধু array/talika বা string-এ কাজ করে, পাওয়া গেছে: {val!r}")

    def _builtin_jog_koro(self, node, env):
        lst = self._eval_args(node, env, 1)[0]
        if not isinstance(lst, list):
            raise BanglaRuntimeError(f"'{node.callee_name}' শুধু array/talika-তে কাজ করে, পাওয়া গেছে: {lst!r}")
        try:
            return sum(lst)
        except TypeError:
            raise BanglaRuntimeError(f"'{node.callee_name}' এর জন্য তালিকার সব মান সংখ্যা হতে হবে")

    def _list_extremum(self, node, env, find_max):
        lst = self._eval_args(node, env, 1)[0]
        if not isinstance(lst, list) or len(lst) == 0:
            raise BanglaRuntimeError(f"'{node.callee_name}' একটা non-empty array/talika চায়")
        try:
            return max(lst) if find_max else min(lst)
        except TypeError:
            raise BanglaRuntimeError(f"'{node.callee_name}' এর জন্য তালিকার সব মান তুলনাযোগ্য হতে হবে")

    def _builtin_ache(self, node, env):
        collection, item = self._eval_args(node, env, 2)
        if isinstance(collection, list):
            return item in collection
        if isinstance(collection, str):
            if not isinstance(item, str):
                raise BanglaRuntimeError(f"String-এ '{node.callee_name}' খোঁজার জন্য দ্বিতীয় argument ও string হতে হবে")
            return item in collection
        raise BanglaRuntimeError(f"'{node.callee_name}' শুধু তালিকা বা লেখার উপর কাজ করে")

    def _builtin_porishor(self, node, env):
        args = self._eval_args(node, env, 1, 3)
        for a in args:
            if not isinstance(a, int) or isinstance(a, bool):
                raise BanglaRuntimeError(f"'{node.callee_name}' এর সব মান পূর্ণসংখ্যা (integer) হতে হবে, পাওয়া গেছে: {a!r}")
        if len(args) == 3 and args[2] == 0:
            raise BanglaRuntimeError(f"'{node.callee_name}' এর step শূন্য (0) হতে পারবে না")
        return list(range(*args))

    def _transform_str(self, node, env, fn):
        val = self._eval_args(node, env, 1)[0]
        if not isinstance(val, str):
            raise BanglaRuntimeError(f"'{node.callee_name}' শুধু string-এ কাজ করে, পাওয়া গেছে: {val!r}")
        return fn(val)

    def _builtin_bhangao(self, node, env):
        args = self._eval_args(node, env, 1, 2)
        text = args[0]
        if not isinstance(text, str):
            raise BanglaRuntimeError(f"'{node.callee_name}' শুধু string-এ কাজ করে, পাওয়া গেছে: {text!r}")
        if len(args) == 1:
            return text.split()
        sep = args[1]
        if not isinstance(sep, str) or sep == "":
            raise BanglaRuntimeError(f"'{node.callee_name}' এর separator non-empty string হতে হবে")
        return text.split(sep)

    def _builtin_purno(self, node, env):
        val = self._eval_args(node, env, 1)[0]
        try:
            return int(val)
        except (ValueError, TypeError):
            raise BanglaRuntimeError(f"{val!r}-কে পূর্ণসংখ্যায় (integer) রূপান্তর করা যায়নি")

    def _builtin_doshomik(self, node, env):
        val = self._eval_args(node, env, 1)[0]
        try:
            return float(val)
        except (ValueError, TypeError):
            raise BanglaRuntimeError(f"{val!r}-কে দশমিক সংখ্যায় (float) রূপান্তর করা যায়নি")

    def _builtin_lekha(self, node, env):
        val = self._eval_args(node, env, 1)[0]
        return self._to_display_string(val)

    def _builtin_dhoron(self, node, env):
        val = self._eval_args(node, env, 1)[0]
        if val is None:
            return "khali"
        if isinstance(val, bool):
            return "shotti_mittha"
        if isinstance(val, (int, float)):
            return "shongkha"
        if isinstance(val, str):
            return "lekha"
        if isinstance(val, list):
            return "talika"
        if isinstance(val, BanglaFunction):
            return "kaj"
        return type(val).__name__

    def _builtin_porom(self, node, env):
        val = self._eval_args(node, env, 1)[0]
        self._check_number(val, node.callee_name)
        return abs(val)

    def _builtin_borgomul(self, node, env):
        val = self._eval_args(node, env, 1)[0]
        self._check_number(val, node.callee_name)
        if val < 0:
            raise BanglaRuntimeError("ঋণাত্মক সংখ্যার বর্গমূল বের করা যায় না")
        res = math.sqrt(val)
        return int(res) if res.is_integer() else res

    def _builtin_ghat(self, node, env):
        base, exp = self._eval_args(node, env, 2)
        self._check_number(base, node.callee_name)
        self._check_number(exp, node.callee_name)
        return base ** exp

    # ---- helpers -----------------------------------------------------
    @staticmethod
    def _is_truthy(value):
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, (str, list)):
            return len(value) > 0
        return True

    @staticmethod
    def _check_number(value, op_name):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise BanglaRuntimeError(
                f"'{op_name}' operator শুধু সংখ্যার (number) জন্য কাজ করে, "
                f"কিন্তু পাওয়া গেছে: {value!r}"
            )

    @staticmethod
    def _to_display_string(value):
        if value is None:
            return "khali"
        if isinstance(value, bool):
            return "shotti" if value else "mittha"
        if isinstance(value, list):
            return "[" + ", ".join(Interpreter._to_display_string(v) for v in value) + "]"
        return str(value)
