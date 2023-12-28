"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """
    # add global sets
    OPS = {'+', '-', '*', '/', '&', '<', '>', '|', '&', '=', "&lt;", "&gt;", "&amp;"}
    UN_OPS = {'-', '~', '^', "#"}
    F_S = {"field", "static"}
    CLASS_OPS = {"constructor", "function", "method"}
    STATEMENTS = {"let", "if", "while", "do", "return"}
    TYPES = {"INT_CONST", "STRING_CONST", "KEYWORD"}

    def __init__(self, input_stream: typing.TextIO,
                 output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        self.class_name = ""
        self.out_file = output_stream
        self.in_file = input_stream
        self.tokenizer = JackTokenizer(input_stream)
        print(self.tokenizer.tokens_from_line)
        self.table = SymbolTable()
        self.vm_writer = VMWriter(self.out_file)
        self.counter = 0

    def __advance(self):
        s = self.tokenizer.peek()
        self.tokenizer.advance()
        return s

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        self.tokenizer.advance()  # class
        self.class_name = self.__advance()  # class name
        print(self.class_name)
        self.tokenizer.advance()  # {
        c = self.tokenizer.peek()
        while c in CompilationEngine.F_S:
            self.compile_class_var_dec()
            c = self.tokenizer.peek()
        while c in CompilationEngine.CLASS_OPS:
            self.compile_subroutine()
            c = self.tokenizer.peek()
        self.tokenizer.advance()  # }
        self.vm_writer.close()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        kind = self.__advance()  # static/field
        type_var = self.__advance()  # type
        name = self.__advance()  # varName
        self.table.define(name, type_var, kind)
        while self.tokenizer.peek() == ",":
            self.__advance()  # ,
            name = self.__advance()  # varName
            self.table.define(name, type_var, kind)
        self.__advance()  # ;

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        # Your code goes here!
        type_function = self.__advance()  # constructor/function/method
        self.__advance()  # void/type*
        sub_name = self.class_name + "." + self.__advance()  # subRoutineName
        self.table.start_subroutine()
        self.__advance()  # (
        self.compile_parameter_list(type_function)  # parameter list
        self.__advance()  # )
        # start:
        self.__advance()  # {

        while self.tokenizer.peek() == "var":
            self.compile_var_dec()
        n = self.table.var_count('var')
        self.vm_writer.write_function(sub_name, n)
        # pointer
        if type_function == 'method':
            self.vm_writer.write_push('argument', 0)
            self.vm_writer.write_pop('pointer', 0)
        elif type_function == "constructor":
            g_args = self.table.var_count('field')
            self.vm_writer.write_push('constant', g_args)
            self.vm_writer.write_call('Memory.alloc', 1)
            self.vm_writer.write_pop('pointer', 0)
        print(self.tokenizer.tokens_from_line[self.tokenizer.c_token])
        print(self.tokenizer.peek())
        self.compile_statements()
        self.__advance()  # }

    def compile_parameter_list(self, type_function) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # Your code goes here!
        next_tok = self.tokenizer.peek()

        if type_function == "method":
            self.table.define("this", "self", "arg")
        if next_tok == ")":
            return
        type_var = self.__advance()  # param type
        name_var = self.__advance()  # name
        self.table.define(name_var, type_var, 'arg')
        while self.tokenizer.peek() == ',':
            self.__advance()  # ,
            type_var = self.__advance()  # param type
            name_var = self.__advance()  # name
            self.table.define(name_var, type_var, 'arg')

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        kind = self.__advance()  # var
        var_type = self.__advance()  # type
        name_var = self.__advance()  # varName
        self.table.define(name_var, var_type, kind)
        while self.tokenizer.peek() == ",":
            self.__advance()  # ,
            # kind = self.__advance()  # var
            name_var = self.__advance()  # varName
            self.table.define(name_var, var_type, kind)
        self.__advance()  # ;

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # Your code goes here!
        p = self.tokenizer.peek()
        while p in CompilationEngine.STATEMENTS:
            if p == "let":
                self.compile_let()
            elif p == "if":
                self.compile_if()
            elif p == "while":
                self.compile_while()
            elif p == "do":
                self.compile_do()
            elif p == "return":
                self.compile_return()
            p = self.tokenizer.peek()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        self.__advance()  # do
        name = self.__advance()  # class_var_name
        func_name = ''
        n = 0  # num of args
        if self.tokenizer.peek() == '.':
            self.__advance()  # .
            func_name = self.__advance()
            type_name = self.table.type_of(name)
            if type_name != "None":
                self.write_push_name(self.table.kind_of(name), self.table.index_of(name))
                name = type_name + "." + func_name
                n = 1
            else:  # Built-in
                name = name + '.' + func_name
        else:
            self.vm_writer.write_push('pointer', 0)
            n = 1
            name = self.class_name + "." + name

        self.__advance()  # (
        n += self.compile_expression_list()
        self.vm_writer.write_call(name, n)
        self.vm_writer.write_pop('temp', 0)
        pp = self.tokenizer.peek()
        self.__advance()  # )
        self.__advance()  # ;
        cp = self.tokenizer.peek()

    def write_push_name(self, k, index):
        if k == 'var':
            self.vm_writer.write_push('local', index)
        elif k == 'arg':
            self.vm_writer.write_push('argument', index)
        elif k == 'static':
            self.vm_writer.write_push('static', index)
        else:
            self.vm_writer.write_push('this', index)

    def write_pop_name(self, k, index):
        if k == 'var':
            self.vm_writer.write_pop('local', index)
        elif k == 'arg':
            self.vm_writer.write_pop('argument', index)
        elif k == 'static':
            self.vm_writer.write_pop('static', index)
        else:
            self.vm_writer.write_pop('this', index)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        self.__advance()  # let
        name = self.__advance()  # varName
        p = self.tokenizer.peek()
        f = False
        if p == "[":
            f = True
            self.__advance()  # [
            self.compile_expression()  # expression
            self.__advance()  # ]
            k = self.table.kind_of(name)
            index = self.table.index_of(name)
            self.write_push_name(k, index)
            self.vm_writer.write_arithmetic("add")

        self.__advance()  # =
        self.compile_expression()  # expression
        if f:
            self.vm_writer.write_pop("temp", 0)
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop("that", 0)
        else:
            k = self.table.kind_of(name)
            index = self.table.index_of(name)
            self.write_pop_name(k, index)
        self.__advance()  # ;

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        counter = self.table.while_counter
        self.vm_writer.write_label("WHILE_START" + str(counter))
        self.__advance()  # while
        self.__advance()  # (
        self.table.while_counter += 1
        self.compile_expression()
        self.vm_writer.write_arithmetic('not')
        self.vm_writer.write_if("WHILE_END" + str(counter))
        self.__advance()  # )
        self.__advance()  # {
        self.compile_statements()
        self.vm_writer.write_goto("WHILE_START" + str(counter))
        self.vm_writer.write_label("WHILE_END" + str(counter))
        self.__advance()  # }

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        self.__advance()  # return
        if self.tokenizer.peek() == ";":
            self.vm_writer.write_push('constant', 0)
        else:
            # while !
            self.compile_expression()
        self.vm_writer.write_return()
        self.__advance()  # ;

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        counter = self.table.if_counter
        self.__advance()  # if
        self.__advance()  # (
        self.compile_expression()
        self.__advance()  # )
        counter = self.table.if_counter

        self.table.if_counter += 1

        self.vm_writer.write_if("IF_TRUE" + str(counter))
        self.vm_writer.write_goto("IF_FALSE" + str(counter))
        self.vm_writer.write_label("IF_TRUE" + str(counter))
        self.__advance()  # {
        r=self.tokenizer.peek()
        self.compile_statements()
        d=self.tokenizer.peek()
        self.__advance()  # }
        c1 = self.tokenizer.peek()
        print(c1)
        if self.tokenizer.peek() == "else":
            print('innnnnnnnnn')
            self.__advance()  # else
            self.vm_writer.write_goto("ELSE" + str(counter))
            self.vm_writer.write_label("IF_FALSE" + str(counter))
            self.__advance()  # {
            self.compile_statements()
            self.__advance()  # }
            self.vm_writer.write_label("ELSE" + str(counter))
        else:
            self.vm_writer.write_label("IF_FALSE" + str(counter))

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # Your code goes here!
        # complete
        self.compile_term()
        c = self.tokenizer.peek()
        while c in CompilationEngine.OPS:
            op = self.__advance()
            self.compile_term()
            if op == "+":
                self.vm_writer.write_arithmetic("add")
            elif op == "-":
                self.vm_writer.write_arithmetic("sub")
            elif op == "*":
                self.vm_writer.write_call("Math.multiply", 2)
            elif op == "/":
                self.vm_writer.write_call("Math.divide", 2)
            elif op == "&":
                self.vm_writer.write_arithmetic("and")
            elif op == "|":
                self.vm_writer.write_arithmetic("or")
            elif op == "<":
                self.vm_writer.write_arithmetic("lt")
            elif op == ">":
                self.vm_writer.write_arithmetic("gt")
            elif op == "=":
                self.vm_writer.write_arithmetic("eq")
            c = self.tokenizer.peek()

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!
        tok = self.tokenizer.peek()
        toke_type = self.tokenizer.peek_token_type(tok)

        if toke_type == "INT_CONST":
            val = self.__advance()
            self.vm_writer.write_push('constant', int(val))

        elif toke_type == "STRING_CONST":
            word = self.__advance()
            self.vm_writer.write_push('constant', len(word))
            self.vm_writer.write_call('String.new', 1)
            for char in word:
                self.vm_writer.write_push('constant', ord(char))
                self.vm_writer.write_call('String.appendChar', 2)
        elif tok in {"true", "false", "null", "this"}:
            k = self.__advance()
            if k != 'this':
                self.vm_writer.write_push('constant', 0)
                if k == "true":
                    self.vm_writer.write_arithmetic('not')
            else:
                self.vm_writer.write_push('pointer', 0)

        # complete
        # toke_type = self.tokenizer.peek_token_type(tok)
        elif toke_type == "IDENTIFIER":
            self.compile_identifier(tok)

        elif self.tokenizer.peek() == "(":
            self.__advance()  # (
            self.compile_expression()
            self.__advance()  # )

        elif self.tokenizer.peek() in CompilationEngine.UN_OPS:
            op = self.__advance()
            self.compile_term()
            if op == '-':
                self.vm_writer.write_arithmetic('neg')
            elif op == '~':
                self.vm_writer.write_arithmetic('not')
            elif op == '^':
                self.vm_writer.write_arithmetic('shiftleft')
            elif op == '#':
                self.vm_writer.write_arithmetic('shiftright')

    def compile_identifier(self, token):
        print('token: ', token)
        name = self.__advance()  # class/var/func name
        n = 0
        is_array = False
        print(self.table.sub_routine_dict)
        if self.tokenizer.peek() == "[":
            is_array = True
            self.__advance()  # [
            self.compile_expression()  # expression
            self.__advance()  # ]
            kind = self.table.kind_of(name)
            if kind != "None":
                self.write_push_name(kind, self.table.index_of(name))
            self.vm_writer.write_arithmetic('add')
        if self.tokenizer.peek() == "(":
            n += 1
            self.__advance()  # (
            self.vm_writer.write_push('pointer', 0)
            n += (self.compile_expression_list())
            self.vm_writer.write_call(self.class_name + "." + name, n)
            self.__advance()  # )

        elif self.tokenizer.peek() == ".":  # subroutine call
            self.__advance()  # .
            sub_name = self.__advance()  # name
            type_name = self.table.type_of(name)
            if type_name != "None":
                self.write_push_name(self.table.kind_of(name), self.table.index_of(name))
                name = type_name + "." + sub_name
                n = 1
            else:  # Built-in
                name = name + '.' + sub_name
            self.__advance()  # (
            n += self.compile_expression_list()
            self.__advance()  # )
            self.vm_writer.write_call(name, n)
        elif is_array:
            self.vm_writer.write_pop('pointer', 1)
            self.vm_writer.write_push('that', 0)
        else:
            kind = self.table.kind_of(name)
            if kind != "None":
                self.write_push_name(kind, self.table.index_of(name))

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        # complete
        if self.tokenizer.peek() == ")":
            return 0
        self.compile_expression()
        n = 1
        while self.tokenizer.peek() == ',':
            self.__advance()  # ,
            self.compile_expression()
            n += 1
        return n
