
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
		letter = plex.Range("AZaz") #letter
		digit = plex.Range("09") #digit

		identifier = letter+plex.Rep(letter|digit) #always starts with letter
		Bool_exp = plex.Str('true','TRUE','True','t','T','false','FALSE','False','f','F','0','1') #t,T,f,F after full words for correct matching

		assign = plex.Str('=')
		parenthesis = plex.Str('(',')')

		keyword = plex.Str('print')
		operator = plex.Str('not','and','or')
		space=plex.Rep1(plex.Any(' \n\t'))

		lexicon = plex.Lexicon([
			(operator,plex.TEXT),
			(parenthesis,plex.TEXT),
			(assign,plex.TEXT),
			(space,plex.IGNORE),
			(keyword, plex.TEXT),
			(Bool_exp,'Bool_exp'),
			(identifier,'id'),
			])
		
		self.scanner = plex.Scanner(lexicon,fp)
		
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
			self.la,self.val = self.next_token()
		else:
			raise ParseError("found {} instead of {}".format(self.la,token))
	
	
	def parse(self,fp):
		""" Creates scanner for input file object fp and calls the parse logic code. """
		
		# create the plex scanner for fp
		self.create_scanner(fp)
		
		# call parsing logic
		self.stmt_list()
	
			
	def stmt_list(self):
		
		if self.la=='id' or self.la=='print':
			self.stmt()
			self.stmt_list()
		elif self.la is None: #epsilon transition 
			return	
		else:
			raise ParseError("ERROR in stmt_list")
			 	
	
	def stmt(self):
		
		if self.la=='id':
			token, text = self.la, self.val 
			print(token, text)
			self.match('id')
			token, text = self.la, self.val
			print(token, text)
			self.match('=')
			self.expr()
		elif self.la == 'print':
			token, text = self.la, self.val
			print(token, text)		
			self.match('print')
			self.expr()
		else:
			raise ParseError("ERROR in stmt")

	
	
	def expr(self):
		
		if self.la=='(' or self.la=='id' or self.la=='Bool_exp' or self.la=='not':
			self.termA()
			self.termA_tail()
		else:
			raise ParseError("ERROR in expr")
			 	

	def termA_tail(self):
		
		if self.la=='or':
			self.operator()
			self.termA()
			self.termA_tail()
		elif self.la == 'and' or self.la == 'not' or self.la == ')' or self.la == 'id' or self.la == 'print' or self.la is None: #epsilon transition
			return
		else:
			raise ParseError("ERROR in termA_tail")


	def termA(self):
		
		if self.la=='(' or self.la=='id' or self.la=='Bool_exp' or self.la=='not':
			self.termB()
			self.termB_tail()
		else:
			raise ParseError("ERROR termA")


	def termB_tail(self):
		
		if self.la=='and':
			self.operator()
			self.termB()
			self.termB_tail()
		elif self.la == 'or' or self.la == 'not' or self.la == ')' or self.la == 'id' or self.la == 'print' or self.la is None: #epsilon transition
			return
		else:
			raise ParseError("ERROR in termB_tail")


	def termB(self):
		
		if self.la=='(' or self.la=='id' or self.la=='Bool_exp':
			self.factor()
		elif self.la=='not':
			self.operator()
			self.factor()
		else:
			raise ParseError("ERROR in termB")




	def factor(self):
		
		if self.la=='(':
			token, text = self.la, self.val
			print(token, text)
			self.match('(')
			self.expr()
			token, text = self.la, self.val
			print(token, text)
			self.match(')')
		elif self.la=='id':
			token, text = self.la, self.val
			print(token, text)
			self.match('id')
			
		elif self.la=='Bool_exp':
			token, text = self.la, self.val
			print(token, text)
			self.match('Bool_exp')


		else:
			raise ParseError ("ERROR in factor")


	def operator(self):
		
		if self.la=='or':
			token, text = self.la, self.val
			print(token, text)
			self.match('or')
		elif self.la=='and':
			token, text = self.la, self.val
			print(token, text)
			self.match('and')
			
		elif self.la=='not':
			token, text = self.la, self.val
			print(token, text)
			self.match('not')

		else:
			raise ParseError ("ERROR")			

		

parser = MyParser()


with open("data.txt","r") as fp:

	try:
		parser.parse(fp)
	except plex.errors.PlexError:
		_,lineno,charno = parser.position()	
		print("Scanner Error: at line {} char {}".format(lineno,charno+1))
	except ParseError as perr:
		_,lineno,charno = parser.position()	
		print("Parser Error: {} at line {} char {}".format(perr,lineno,charno+1))
