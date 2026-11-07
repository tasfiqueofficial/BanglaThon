"""
Interpreter for Bangla Programming Language
==============================================
Kaj: Parser-er AST tree "walk" kore actual execution kora — variable e
value rakha, condition check kora, loop chalano, function call kora,
ar screen-e output dekhano.

Eita "Tree-Walking Interpreter" pattern use kore: প্রতিটা node type-এর
জন্য একটা visit_XxxNode method ache, jeta সেই node-টার কাজ actually করে।
"""

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


# ---------------------------------------------------------
# Runtime errors & control-flow signals
# ---------------------------------------------------------
class BanglaRuntimeError(Exception):
    """Actual error dekhano user-ke, jemon: variable na thakle, type mismatch hole."""
    pass


class BreakSignal(Exception):
    """thamo (break) hole ei signal internally throw hoy, loop-er kach theke dhora hoy."""
    pass


class ContinueSignal(Exception):
    """cholo (continue) hole ei signal throw hoy."""
    pass


class ReturnSignal(Exception):
    """ferot (return) hole ei signal throw hoy, function call-er kache dhora hoy."""
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
        self.closure_env = closure_env  # jekhane function-ta define hoyeche

    def __repr__(self):
        return f"<function {self.name}>"


# ---------------------------------------------------------
# Interpreter
# ---------------------------------------------------------
class Interpreter:
    def __init__(self):
        self.global_env = Environment()

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
        if isinstance(collection, str):
            self._check_index(collection, index)
            return collection[int(index)]
        if isinstance(collection, list):
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
            if not self._is_truthy(left):
                return False
            right = self._evaluate(node.right, env)
            return self._is_truthy(right)
        if op == "OR":
            left = self._evaluate(node.left, env)
            if self._is_truthy(left):
                return True
            right = self._evaluate(node.right, env)
            return self._is_truthy(right)

        left = self._evaluate(node.left, env)
        right = self._evaluate(node.right, env)

        if op == "PLUS":
            if isinstance(left, str) or isinstance(right, str):
                return self._to_display_string(left) + self._to_display_string(right)
            return left + right
        if op == "MINUS":
            self._check_number(left, "-"); self._check_number(right, "-")
            return left - right
        if op == "STAR":
            self._check_number(left, "*"); self._check_number(right, "*")
            return left * right
        if op == "SLASH":
            self._check_number(left, "/"); self._check_number(right, "/")
            if right == 0:
                raise BanglaRuntimeError("শূন্য দিয়ে ভাগ করা যায় না (division by zero)")
            return left / right
        if op == "PERCENT":
            self._check_number(left, "%"); self._check_number(right, "%")
            return left % right
        if op == "GT":
            return left > right
        if op == "LT":
            return left < right
        if op == "GTE":
            return left >= right
        if op == "LTE":
            return left <= right
        if op == "EQ":
            return left == right
        if op == "NEQ":
            return left != right

        raise BanglaRuntimeError(f"Unknown binary operator: {op}")

    def _eval_CallNode(self, node, env):
        # built-in: nao (input)
        if node.callee_name == "nao":
            prompt = ""
            if node.arguments:
                prompt = self._to_display_string(self._evaluate(node.arguments[0], env))
            user_input = input(prompt)
            return user_input

        # built-in: dhoirgo (length) — works on list or string
        if node.callee_name == "dhoirgo":
            self._require_arg_count(node, 1)
            val = self._evaluate(node.arguments[0], env)
            if isinstance(val, (list, str)):
                return len(val)
            raise BanglaRuntimeError(f"'dhoirgo' শুধু array/talika বা string-এ কাজ করে, পাওয়া গেছে: {val!r}")

        # built-in: juktokoro (push/append to end of list) — mutates in place
        if node.callee_name == "juktokoro":
            self._require_arg_count(node, 2)
            lst = self._evaluate(node.arguments[0], env)
            value = self._evaluate(node.arguments[1], env)
            if not isinstance(lst, list):
                raise BanglaRuntimeError(f"'juktokoro' শুধু array/talika-তে কাজ করে, পাওয়া গেছে: {lst!r}")
            lst.append(value)
            return lst

        # built-in: shajao (sort) — returns a NEW sorted list (non-mutating)
        if node.callee_name == "shajao":
            self._require_arg_count(node, 1)
            lst = self._evaluate(node.arguments[0], env)
            if not isinstance(lst, list):
                raise BanglaRuntimeError(f"'shajao' শুধু array/talika-তে কাজ করে, পাওয়া গেছে: {lst!r}")
            try:
                return sorted(lst)
            except TypeError:
                raise BanglaRuntimeError("'shajao' এর জন্য array-এর সব element একই ধরনের হতে হবে")

        # built-in: ulto (reverse) — returns a NEW reversed list
        if node.callee_name == "ulto":
            self._require_arg_count(node, 1)
            lst = self._evaluate(node.arguments[0], env)
            if isinstance(lst, list):
                return list(reversed(lst))
            if isinstance(lst, str):
                return lst[::-1]
            raise BanglaRuntimeError(f"'ulto' শুধু array/talika বা string-এ কাজ করে, পাওয়া গেছে: {lst!r}")

        # built-in: jog_koro (sum of all elements)
        if node.callee_name == "jog_koro":
            self._require_arg_count(node, 1)
            lst = self._evaluate(node.arguments[0], env)
            if not isinstance(lst, list):
                raise BanglaRuntimeError(f"'jog_koro' শুধু array/talika-তে কাজ করে, পাওয়া গেছে: {lst!r}")
            return sum(lst)

        # built-in: shorbo_boro (max) / shorbo_choto (min)
        if node.callee_name in ("shorbo_boro", "shorbo_choto"):
            self._require_arg_count(node, 1)
            lst = self._evaluate(node.arguments[0], env)
            if not isinstance(lst, list) or len(lst) == 0:
                raise BanglaRuntimeError(f"'{node.callee_name}' একটা non-empty array/talika চায়")
            return max(lst) if node.callee_name == "shorbo_boro" else min(lst)

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

        return None  # function er kono explicit return na thakle

    # ---- helpers -----------------------------------------------------
    @staticmethod
    def _require_arg_count(node, expected):
        if len(node.arguments) != expected:
            raise BanglaRuntimeError(
                f"'{node.callee_name}' এর {expected} টা argument দরকার, "
                f"কিন্তু {len(node.arguments)} টা দেওয়া হয়েছে"
            )

    @staticmethod
    def _is_truthy(value):
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        if isinstance(value, list):
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
