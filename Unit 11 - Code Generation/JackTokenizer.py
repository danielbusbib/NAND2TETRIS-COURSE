"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    """
    KEYWORDS = {"class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean",
                "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"}
    SYMBOL = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '<', '>', '=', '~', '#', '^', '|'}

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is:
        self.tokens_from_line = []
        self.data = input_stream.read().splitlines()
        print(self.data)
        self.line = 0
        self.peeked = 0
        self.c_token = -1
        self.cur_line = self.data[0]
        self._split_line_to_tokens()

    def _split_line_to_tokens(self):
        stringy = ""
        self.tokens_from_line = []
        flag = False
        # print('pp ', self.cur_line)
        for line in self.data:
            self.cur_line = " ".join(line.split('\t'))
            if '/*' in self.cur_line and '*/' in self.cur_line:
                p = self.cur_line.find('*/')
                k = self.cur_line.find('/*')
                self.cur_line = self.cur_line[:k] + self.cur_line[p + 2:]
                j = len(self.cur_line)
            if '/**' in self.cur_line[:]:
                k = self.cur_line.find('/**')
                if self.cur_line[:k] == " " * len(self.cur_line[:k]):
                    flag = True
            if '/*' in self.cur_line[:]:
                k = self.cur_line.find('/*')
                if self.cur_line[:k] == " " * len(self.cur_line[:k]):
                    flag = True
            if flag:
                if '*/' in self.cur_line:
                    flag = False
                continue
            if "*" in self.cur_line[:]:
                k = self.cur_line.find('*')
                if self.cur_line[:k] == " " * len(self.cur_line[:k]):
                    continue
            j = len(self.cur_line)
            if "//" in self.cur_line:
                j = self.cur_line.find("//")
            elif '/**' in self.cur_line:
                j = self.cur_line.find('/**')
            elif '/*' in self.cur_line:
                j = self.cur_line.find('/*')

            for c in self.cur_line[:j]:
                if "//" in stringy:
                    break
                if stringy and stringy[0] == '"':
                    stringy += c
                    if c == '"':
                        self.tokens_from_line.append(stringy)
                        stringy = ""
                    continue
                if c != ' ':
                    stringy += c
                if stringy == '\t':
                    stringy = ''
                if c in JackTokenizer.SYMBOL or c in JackTokenizer.KEYWORDS:
                    if stringy[:-1] != "":
                        self.tokens_from_line.append(stringy[:-1])
                    self.tokens_from_line.append(c)
                    stringy = ""
                elif c == ' ':
                    if stringy == "":
                        continue
                    if stringy[0] == '"':
                        stringy += ' '
                        continue
                    self.tokens_from_line.append(stringy)
                    stringy = ""
            if stringy:
                self.tokens_from_line.append(stringy)
                stringy = ""

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # Your code goes here!
        if self.line == len(self.data) and self.c_token == len(self.tokens_from_line):
            return False
        return True

    def peek(self, ad=None) -> str:
        if self.has_more_tokens():
            return self.tokens_from_line[self.c_token + 1]

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        # Your code goes here!
        self.c_token += 1

    def peek_token_type(self, tok) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        if tok in JackTokenizer.SYMBOL:
            return "SYMBOL"
        if tok in JackTokenizer.KEYWORDS:
            return "KEYWORD"
        if tok.isnumeric() and abs(int(tok)) < 32167:
            return "INT_CONST"
        if tok[0] == '"' and tok[-1] == '"':
            return "STRING_CONST"
        return "IDENTIFIER"

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        tok = self.tokens_from_line[self.c_token]
        if not tok:
            return
        if tok in JackTokenizer.SYMBOL:
            return "SYMBOL"
        if tok in JackTokenizer.KEYWORDS:
            return "KEYWORD"
        if tok.isnumeric() and abs(int(tok)) < 32167:
            return "INT_CONST"
        if tok[0] == '"' and tok[-1] == '"':
            return "STRING_CONST"
        return "IDENTIFIER"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        return self.tokens_from_line[self.c_token]

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        # Your code goes here!
        value = self.tokens_from_line[self.c_token]
        if value == '<':
            return '&lt;'
        elif value == '>':
            return '&gt;'
        elif value == '"':
            return '&quot;'
        elif value == '&':
            return '&amp;'
        return value

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        # Your code goes here!
        return self.tokens_from_line[self.c_token]

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        # Your code goes here!
        return int(self.tokens_from_line[self.c_token])

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        # Your code goes here!
        return self.tokens_from_line[self.c_token][1:-1]
