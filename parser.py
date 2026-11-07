"""
Parser for Bangla Programming Language
=========================================
Kaj: Lexer-er token gulo niye "recursive descent parsing" diye
AST (Abstract Syntax Tree) banano.

Recursive Descent মানে: প্রতিটা grammar rule-এর জন্য একটা আলাদা function
থাকে, ar function গুলো একে অপরকে call করে (recursive) — ঠিক grammar-এর
nested structure-এর মতো।

Grammar precedence (niche theke upor e — nicher gula age evaluate hoy):
    or_expr    -> and_expr (('ba' | OR) and_expr)*
    and_expr   -> not_expr (('ebong' | AND) not_expr)*
    not_expr   -> ('noy' | NOT) not_expr | comparison
    comparison -> addition ((> | < | >= | <= | == | !=) addition)*
    addition   -> term ((+ | -) term)*
    term       -> factor ((* | / | %) factor)*
    factor     -> NUMBER | STRING | IDENTIFIER | '(' or_expr ')' | call | list
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


class ParserError(Exception):
    def __init__(self, message, line=None, col=None):
        loc = f" (line {line}, col {col})" if line else ""
        super().__init__(f"Parser Error{loc}: {message}")


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ---- helpers ---------------------------------------------------
    def _peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def _current(self):
        return self._peek()

    def _advance(self):
        tok = self._peek()
        if tok.type != "EOF":
            self.pos += 1
        return tok

    def _check(self, *types):
        return self._peek().type in types

    def _match(self, *types):
        if self._check(*types):
            return self._advance()
        return None

    def _expect(self, type_, message=None):
        if self._check(type_):
            return self._advance()
        tok = self._peek()
        msg = message or f"Expected {type_} but got {tok.type} ({tok.value!r})"
        raise ParserError(msg, tok.line, tok.col)

    def _skip_newlines(self):
        while self._check("NEWLINE"):
            self._advance()

    # ---- entry point -------------------------------------------------
    def parse(self):
        statements = []
        self._skip_newlines()
        while not self._check("EOF"):
            stmt = self._statement()
            if stmt is not None:
                statements.append(stmt)
            self._skip_newlines()
        return ProgramNode(statements)

    # ---- statements ----------------------------------------------------
    def _statement(self):
        tok = self._peek()

        if tok.type == "DHORI":
            return self._var_decl()
        if tok.type == "JODI":
            return self._if_statement()
        if tok.type == "JOTOKKHON":
            return self._while_statement()
        if tok.type == "JONNO":
            return self._for_statement()
        if tok.type == "KAJ":
            return self._function_def()
        if tok.type == "FEROT":
            return self._return_statement()
        if tok.type == "DEKHAO":
            return self._print_statement()
        if tok.type == "BREAK":
            self._advance()
            return BreakNode()
        if tok.type == "CONTINUE":
            self._advance()
            return ContinueNode()
        if tok.type == "IDENTIFIER" and self._peek(1).type == "ASSIGN":
            return self._assignment()
        if tok.type == "IDENTIFIER" and self._peek(1).type == "LBRACKET":
            # could be index-assignment (nums[0] = 5) or just an expression statement (nums[0])
            saved_pos = self.pos
            expr = self._or_expr()
            if isinstance(expr, IndexNode) and self._check("ASSIGN"):
                self._advance()  # consume '='
                value_expr = self._or_expr()
                return IndexAssignNode(expr.collection, expr.index_expr, value_expr)
            return ExpressionStatementNode(expr)

        # fallback: expression statement (e.g. calling a function alone)
        expr = self._or_expr()
        return ExpressionStatementNode(expr)

    def _block(self):
        """{ statement* } — returns a list of statements"""
        self._expect("LBRACE", "Expected '{' to start a block")
        self._skip_newlines()
        statements = []
        while not self._check("RBRACE") and not self._check("EOF"):
            stmt = self._statement()
            if stmt is not None:
                statements.append(stmt)
            self._skip_newlines()
        self._expect("RBRACE", "Expected '}' to close a block")
        return statements

    def _var_decl(self):
        self._expect("DHORI")
        name_tok = self._expect("IDENTIFIER", "Expected variable name after 'dhori'")
        self._expect("ASSIGN", f"Expected '=' after variable name '{name_tok.value}'")
        value_expr = self._or_expr()
        return VarDeclNode(name_tok.value, value_expr)

    def _assignment(self):
        name_tok = self._expect("IDENTIFIER")
        self._expect("ASSIGN")
        value_expr = self._or_expr()
        return AssignNode(name_tok.value, value_expr)

    def _print_statement(self):
        self._expect("DEKHAO")
        expr = self._or_expr()
        return PrintNode(expr)

    def _if_statement(self):
        self._expect("JODI")
        self._expect("LPAREN", "Expected '(' after 'jodi'")
        condition = self._or_expr()
        self._expect("RPAREN", "Expected ')' after condition")
        self._skip_newlines()
        then_branch = self._block()
        self._skip_newlines()

        else_branch = None
        if self._check("NAHOLE"):
            self._advance()
            self._skip_newlines()
            if self._check("JODI"):
                # 'nahole jodi' -> else-if, represented as a nested IfNode
                else_branch = [self._if_statement()]
            else:
                else_branch = self._block()

        return IfNode(condition, then_branch, else_branch)

    def _while_statement(self):
        self._expect("JOTOKKHON")
        self._expect("LPAREN", "Expected '(' after 'jotokkhon'")
        condition = self._or_expr()
        self._expect("RPAREN", "Expected ')' after condition")
        self._skip_newlines()
        body = self._block()
        return WhileNode(condition, body)

    def _for_statement(self):
        self._expect("JONNO")
        self._expect("LPAREN", "Expected '(' after 'jonno'")

        # init: either a var-decl or an assignment
        if self._check("DHORI"):
            init = self._var_decl()
        else:
            init = self._assignment()
        self._expect("SEMICOLON", "Expected ';' after for-loop init")

        condition = self._or_expr()
        self._expect("SEMICOLON", "Expected ';' after for-loop condition")

        # update: an assignment, no trailing semicolon
        update = self._assignment()

        self._expect("RPAREN", "Expected ')' to close for-loop header")
        self._skip_newlines()
        body = self._block()
        return ForNode(init, condition, update, body)

    def _function_def(self):
        self._expect("KAJ")
        name_tok = self._expect("IDENTIFIER", "Expected function name after 'kaj'")
        self._expect("LPAREN", "Expected '(' after function name")
        params = []
        if not self._check("RPAREN"):
            params.append(self._expect("IDENTIFIER").value)
            while self._match("COMMA"):
                params.append(self._expect("IDENTIFIER").value)
        self._expect("RPAREN", "Expected ')' after parameter list")
        self._skip_newlines()
        body = self._block()
        return FunctionDefNode(name_tok.value, params, body)

    def _return_statement(self):
        self._expect("FEROT")
        # 'ferot' with no expression -> return null
        if self._check("NEWLINE", "RBRACE", "EOF"):
            return ReturnNode(None)
        expr = self._or_expr()
        return ReturnNode(expr)

    # ---- expressions (precedence climbing) ------------------------------
    def _or_expr(self):
        left = self._and_expr()
        while self._check("OR"):
            op = self._advance()
            right = self._and_expr()
            left = BinaryOpNode(left, op.type, right)
        return left

    def _and_expr(self):
        left = self._not_expr()
        while self._check("AND"):
            op = self._advance()
            right = self._not_expr()
            left = BinaryOpNode(left, op.type, right)
        return left

    def _not_expr(self):
        if self._check("NOT"):
            op = self._advance()
            operand = self._not_expr()
            return UnaryOpNode(op.type, operand)
        return self._comparison()

    def _comparison(self):
        left = self._addition()
        while self._check("GT", "LT", "GTE", "LTE", "EQ", "NEQ"):
            op = self._advance()
            right = self._addition()
            left = BinaryOpNode(left, op.type, right)
        return left

    def _addition(self):
        left = self._term()
        while self._check("PLUS", "MINUS"):
            op = self._advance()
            right = self._term()
            left = BinaryOpNode(left, op.type, right)
        return left

    def _term(self):
        left = self._unary()
        while self._check("STAR", "SLASH", "PERCENT"):
            op = self._advance()
            right = self._unary()
            left = BinaryOpNode(left, op.type, right)
        return left

    def _unary(self):
        if self._check("MINUS"):
            op = self._advance()
            operand = self._unary()
            return UnaryOpNode(op.type, operand)
        return self._call_or_primary()

    def _call_or_primary(self):
        expr = self._primary()
        # function-call syntax: identifier immediately followed by '('
        if isinstance(expr, IdentifierNode) and self._check("LPAREN"):
            self._advance()
            args = []
            if not self._check("RPAREN"):
                args.append(self._or_expr())
                while self._match("COMMA"):
                    args.append(self._or_expr())
            self._expect("RPAREN", "Expected ')' to close function call")
            expr = CallNode(expr.name, args)

        # indexing syntax: expr[index], chainable for nested arrays e.g. matrix[0][1]
        while self._check("LBRACKET"):
            self._advance()
            index_expr = self._or_expr()
            self._expect("RBRACKET", "Expected ']' to close index")
            expr = IndexNode(expr, index_expr)

        return expr

    def _primary(self):
        tok = self._peek()

        if tok.type == "NUMBER":
            self._advance()
            return NumberNode(tok.value)

        if tok.type == "STRING":
            self._advance()
            return StringNode(tok.value)

        if tok.type == "TRUE":
            self._advance()
            return BooleanNode(True)

        if tok.type == "FALSE":
            self._advance()
            return BooleanNode(False)

        if tok.type == "NULL":
            self._advance()
            return NullNode()

        if tok.type == "TALIKA":
            self._advance()
            self._expect("LPAREN", "Expected '(' after 'talika'")
            elements = []
            if not self._check("RPAREN"):
                elements.append(self._or_expr())
                while self._match("COMMA"):
                    elements.append(self._or_expr())
            self._expect("RPAREN", "Expected ')' to close list")
            return ListNode(elements)

        if tok.type == "NAO":
            self._advance()
            self._expect("LPAREN", "Expected '(' after 'nao'")
            prompt_expr = None
            if not self._check("RPAREN"):
                prompt_expr = self._or_expr()
            self._expect("RPAREN", "Expected ')' to close 'nao'")
            return CallNode("nao", [prompt_expr] if prompt_expr else [])

        if tok.type == "IDENTIFIER":
            self._advance()
            return IdentifierNode(tok.value)

        if tok.type == "LPAREN":
            self._advance()
            expr = self._or_expr()
            self._expect("RPAREN", "Expected ')' to close expression")
            return expr

        raise ParserError(
            f"Unexpected token {tok.type} ({tok.value!r})", tok.line, tok.col
        )
