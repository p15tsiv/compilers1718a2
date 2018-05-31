import plex

class ParseError(Exception):
	""" A user defined exception class, to describe parse errors. """
	pass

class MyParser:
	""" A class encapsulating all parsing functionality
	for a particular grammar. """
	
	def create_scanner(self,fp):
		""" Creates a plex scanner for a particular grammar 
		to operate on file object fp. """

		# define some pattern constructs
		letter = plex.Range("AZaz")
		digit = plex.Range("09")

		variable = letter + plex.Rep(letter | digit)
		true = plex.NoCase(plex.Str("true","t","1")) 
		false = plex.NoCase(plex.Str("false","f","0"))
		
		assign = plex.Str("=")
		op = plex.Str("not","and","or")

		parenthesis = plex.Str("(",")")
		keyword = plex.Str("print")		
		space = plex.Any(" \t\n")

		# the scanner lexicon - constructor argument is a list of (pattern,action ) tuples
		lexicon = plex.Lexicon([
			(op,plex.TEXT),
			(true,'TRUE'),
			(false,'FALSE'),
			(assign, plex.TEXT),
			(parenthesis,plex.TEXT),
			(space,plex.IGNORE),
			(keyword, plex.TEXT),
			(variable, 'VARIABLE')
			])
		
		# create and store the scanner object
		self.scanner = plex.Scanner(lexicon,fp)
		
		# get initial lookahead
		self.la,self.val = self.next_token()

	def next_token(self):
		""" Returns tuple (next_token,matched-text). """
		
		return self.scanner.read()		

	def position(self):
		""" Utility function that returns position in text in case of errors.
		Here it simply returns the scanner position. """
		
		return self.scanner.position()

	def match(self,token):
		""" Consumes (matches with current lookahead) an expected token.
		Raises ParseError if anything else is found. Acquires new lookahead. """ 
		
		if self.la==token:
			print("FOUND:	",self.val)
			self.la,self.val = self.next_token()
			
		else:
			raise ParseError("found {} instead of {}".format(self.la,token))

	def parse(self,fp):
		""" Creates scanner for input file object fp and calls the parse logic code. """
		
		# create the plex scanner for fp
		# call parsing logic
		self.create_scanner(fp)
		self.stmt_list()

	def stmt_list(self):
		if self.la=='VARIABLE' or self.la=='print':
			self.stmt()
			self.stmt_list()
		elif self.la is None:
			return
		else:
			raise ParseError("stmt_list() Error, expected one of the following: 'variable', 'print'")


	def stmt(self):
		if self.la=='VARIABLE':
			self.match('VARIABLE')
			self.match('=')
			self.expr()
		elif self.la=='print':
			self.match('print')
			self.expr()
		else:
			raise ParseError("stmt() Error, expected one of the following: 'variable', '=', 'print'")


	def expr(self):
		if self.la=='(' or self.la=='VARIABLE' or self.la=='TRUE' or self.la=='FALSE' or 'not':
			self.termA()
			self.termA_tail()
		else:
			raise ParseError("expr() Error, expected one of the following: '(', 'variable', 'boolean', 'not'")


	def termA_tail(self):
		if self.la=='or':
			self.operator()
			self.termA()
			self.termA_tail()
		elif self.la==')' or self.la=='VARIABLE' or self.la == 'print': #apo to follow set tou termA_tal
			return 
		elif self.la is None:
			return	
		else:
			raise ParseError("termA_tail() Error, expected one of the following: 'or', ')', 'variable', 'print'")

	def termA(self):
		if self.la=='(' or self.la=='VARIABLE' or self.la=='TRUE' or self.la=='FALSE' or 'not':
			self.operator()
			self.factor()
			self.factor_tail()
		else:
			raise ParseError("termA() Error, expected one of the following: '(', 'variable', 'boolean', 'not'")

	def factor_tail(self):
		if self.la=='and':
			self.operator()
			self.factor()
			self.factor_tail()
		if self.la == 'VARIABLE' or  self.la == 'or'  or  self.la == ')'  or  self.la == 'print' : #apo to follow set tou factor_tail
			return
		if self.la is None:
			return
		else:
			raise ParseError("factor_tail() Error, expected one of the following: 'and', 'or', 'variable', ')' or 'print'")

	def factor(self):
		if self.la=='(':
			self.match('(')
			self.expr()
			self.match(')')
		elif self.la=='VARIABLE':
			self.match('VARIABLE')
		elif self.la=='TRUE' or self.la=='FALSE':
			self.boolean()
		else:
			raise ParseError("factor() Error, expected one of the following: '(', 'variable', 'boolean'")


	def boolean(self):
		if self.la=='TRUE':
			self.match('TRUE')
		elif self.la=='FALSE':
			self.match('FALSE')
		else:
			raise ParseError("boolean() Error, expected one of the following: 'true', 'false'")


	def operator(self):
		if self.la=='or':
			self.match('or')
		elif self.la=='and':
			self.match('and')
		elif self.la=='not':
				self.match('not')
		else:
			return

# the main part of prog

# create the parser object
parser = MyParser()

# open file for parsing
with open("data.txt","r") as fp:

	# parse file
	try:
		parser.parse(fp)
	except plex.errors.PlexError:
		_,lineno,charno = parser.position()	
		print("Scanner Error: at line {} char {}".format(lineno,charno+1))
	except ParseError as perr:
		_,lineno,charno = parser.position()	
		print("Parser Error: {} at line {} char {}".format(perr,lineno,charno+1))