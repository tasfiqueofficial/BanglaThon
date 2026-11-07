"""
AST (Abstract Syntax Tree) Node Definitions
=============================================
Eগুলো হলো "বাক্যের গঠন" মনে রাখার জন্য ছোট ছোট বাক্স।

Jemon: "jodi (x > 5) { dekhao "hi" }"
eita ekটা IfNode হয়ে সংরক্ষিত হবে, যার ভেতরে থাকবে:
  - condition: x > 5 (ekটা BinaryOpNode)
  - then_branch: [dekhao "hi"] (statement-er list)
"""


# ---------------------------------------------------------
# Base class (সব node এর common ancestor)
# ---------------------------------------------------------
class Node:
    pass


# ---------------------------------------------------------
# Expressions (মান যা একটা VALUE বের করে দেয়)
# ---------------------------------------------------------
class NumberNode(Node):
    def __init__(self, value):
        self.value = value  # 10, 3.14

    def __repr__(self):
        return f"Number({self.value})"


class StringNode(Node):
    def __init__(self, value):
        self.value = value  # "Tasfique"

    def __repr__(self):
        return f"String({self.value!r})"


class BooleanNode(Node):
    def __init__(self, value):
        self.value = value  # True / False (shotti/mittha)

    def __repr__(self):
        return f"Boolean({self.value})"


class NullNode(Node):
    def __repr__(self):
        return "Null"


class ListNode(Node):
    def __init__(self, elements):
        self.elements = elements  # list of expression nodes

    def __repr__(self):
        return f"List({self.elements})"


class IdentifierNode(Node):
    def __init__(self, name):
        self.name = name  # variable-er naam, jemon "x"

    def __repr__(self):
        return f"Identifier({self.name})"


class BinaryOpNode(Node):
    """Duita jinis er modde operation, jemon: x + 5, x > 5, a ebong b"""
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator  # '+', '>', 'AND', etc.
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left} {self.operator} {self.right})"


class UnaryOpNode(Node):
    """Ekta jinis er upore operation, jemon: -x, noy x"""
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp({self.operator} {self.operand})"


class IndexNode(Node):
    """Array/list-er element access, jemon: nums[0]"""
    def __init__(self, collection, index_expr):
        self.collection = collection      # expression jeta list/array dey
        self.index_expr = index_expr      # index-er value

    def __repr__(self):
        return f"Index({self.collection}[{self.index_expr}])"


class IndexAssignNode(Node):
    """Array-er element-e value bosano, jemon: nums[0] = 5"""
    def __init__(self, collection, index_expr, value_expr):
        self.collection = collection
        self.index_expr = index_expr
        self.value_expr = value_expr

    def __repr__(self):
        return f"IndexAssign({self.collection}[{self.index_expr}] = {self.value_expr})"


class CallNode(Node):
    """Function call, jemon: jog(2, 3) ba dekhao("hi")"""
    def __init__(self, callee_name, arguments):
        self.callee_name = callee_name  # function-er naam
        self.arguments = arguments      # list of expression nodes

    def __repr__(self):
        return f"Call({self.callee_name}, {self.arguments})"


# ---------------------------------------------------------
# Statements (কাজ যা করা হয়, মান ফেরত দেয় না)
# ---------------------------------------------------------
class VarDeclNode(Node):
    """dhori x = 10"""
    def __init__(self, name, value_expr):
        self.name = name
        self.value_expr = value_expr

    def __repr__(self):
        return f"VarDecl({self.name} = {self.value_expr})"


class AssignNode(Node):
    """x = 20  (already declared variable-e notun value bosano)"""
    def __init__(self, name, value_expr):
        self.name = name
        self.value_expr = value_expr

    def __repr__(self):
        return f"Assign({self.name} = {self.value_expr})"


class PrintNode(Node):
    """dekhao "hi" """
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"Print({self.expr})"


class IfNode(Node):
    """jodi (...) { ... } nahole jodi (...) { ... } nahole { ... }"""
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch    # list of statements
        self.else_branch = else_branch    # list of statements OR another IfNode OR None

    def __repr__(self):
        return f"If({self.condition}, then={self.then_branch}, else={self.else_branch})"


class WhileNode(Node):
    """jotokkhon (...) { ... }"""
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body  # list of statements

    def __repr__(self):
        return f"While({self.condition}, {self.body})"


class ForNode(Node):
    """jonno (init; condition; update) { ... }"""
    def __init__(self, init, condition, update, body):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

    def __repr__(self):
        return f"For({self.init}; {self.condition}; {self.update}, {self.body})"


class FunctionDefNode(Node):
    """kaj jog(a, b) { ferot a + b }"""
    def __init__(self, name, params, body):
        self.name = name
        self.params = params  # list of parameter names
        self.body = body      # list of statements

    def __repr__(self):
        return f"FunctionDef({self.name}({self.params}), {self.body})"


class ReturnNode(Node):
    """ferot x"""
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"Return({self.expr})"


class BreakNode(Node):
    """thamo"""
    def __repr__(self):
        return "Break"


class ContinueNode(Node):
    """cholo"""
    def __repr__(self):
        return "Continue"


class ExpressionStatementNode(Node):
    """Ekta expression jeta statement hishebe use hoyeche, jemon: jog(2,3) (return value use hoyni)"""
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"ExprStmt({self.expr})"


class ProgramNode(Node):
    """Puro program — statement-er ekta list"""
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements})"
