lexer grammar languageLexer ;


// Rules prefixed with fragment can be called only from other lexer rules;
// they are not tokens in their own right.

// Separators

MINUS
    : '-' ;

PLUS
    : '+' ;

TIMES
    : '*' ;

DIVIDE
    : '/' ;

LPAREN
	: '(' ;

RPAREN
	: ')' ;

LBRACE
	: '{' ;

RBRACE
	: '}' ;

LBRACK
	: '[' ;

RBRACK
	: ']' ;

SEMICOLON
	: ';' ;

COLON
	: ':' ;

COMMA
	: ',' ;

DOT
	: '.' ;

MILES
    : ('Mi' | 'miles') ;

KILOMETERS
    : ('KM' | 'kilometers');

MINUTE
	: 'm' ;

SEC
    : 's' ;

MSEC
    : 'ms' ;


OPERATOR
    : UntilOperator
    | AndOperator
    | OccurAroundOperator ;

NotOperator
	: 'not' | '!';

OrOperator
	: 'or' | '|';

WithinOperator
	: 'within' | 'W' ;

OverlapOperator
	: 'overlap' | 'O';

UntilOperator
	: 'until' | 'U' ;

AndOperator
	: 'and' | '&' ;

OccurAroundOperator
	: 'occur_around';


EqualOperator
	: '==' ;

NotEqualOperator
	: '!=' ;

GreaterOrEqualOperator
	: '>=' ;

LesserOrEqualOperator
	: '<=' ;

GreaterOperator
	: '>' ;

LesserOperator
	: '<' ;

EQUAL
	: '=' ;


// Properties of entities
EntityType
	: 'type' ;

EntityLocation
	: 'location';

GroupMemberDistances
	: 'member_distances';

GroupPositions
	: 'positions';


// Adding some special tags
CONSTRAINT_TAG
	: 'constraint' ;

SPATIAL_TAG
	: 'spatial_event';


// ADDING ATTRIBUTES
REID_ATTRIBUTES
  : ('object_type' | 'color') ;


// Literals
BooleanLiteral
	: (TRUE | FALSE) ;

TRUE
	: ('true' | 'TRUE');

FALSE
	: ('false' | 'FALSE');

Infinity
  : ('+inf' | '-inf');

IntegerLiteral
	: DecimalNumeral
	| HexNumeral
	| BinaryNumeral ;

fragment DecimalNumeral
	: '0'
	| NonZeroDigit (Digits? | Underscores Digits) ;

fragment Digits
	: Digit (DigitsAndUnderscores? Digit)? ;

fragment Digit
	: '0'
	| NonZeroDigit ;

fragment NonZeroDigit
	: [1-9] ;

fragment DigitsAndUnderscores
	: DigitOrUnderscore+ ;

fragment DigitOrUnderscore
	: Digit
	| '_' ;

fragment Underscores
	: '_'+ ;

fragment HexNumeral
	: '0' [xX] HexDigits ;

fragment HexDigits
	: HexDigit (HexDigitsAndUnderscores? HexDigit)? ;

fragment HexDigit
	: [0-9a-fA-F] ;

fragment HexDigitsAndUnderscores
	: HexDigitOrUnderscore+ ;

fragment HexDigitOrUnderscore
	: HexDigit
	| '_' ;

fragment BinaryNumeral
	: '0' [bB] BinaryDigits ;

fragment BinaryDigits
	: BinaryDigit (BinaryDigitsAndUnderscores? BinaryDigit)? ;

fragment BinaryDigit
	: [01] ;

fragment BinaryDigitsAndUnderscores
	: BinaryDigitOrUnderscore+ ;


fragment BinaryDigitOrUnderscore
	: BinaryDigit
	| '_' ;

RealLiteral
	: DecimalRealLiteral ;

fragment DecimalRealLiteral
	: Digits '.' Digits? ExponentPart?
	| '.' Digits ExponentPart?
	| Digits ExponentPart
	;

fragment ExponentPart
	: ExponentIndicator SignedInteger ;

fragment ExponentIndicator
	: [eE] ;

fragment SignedInteger
	: Sign? Digit+ ;

fragment Sign
	: [+-] ;


Identifier
	: ((IdentifierStart)(IdentifierPart)*) ;


fragment IdentifierStart
	: (LetterOrUnderscore | '$') ;

fragment IdentifierPart
	: ( IdentifierStart | Digit | '.' | '/' ) ;

fragment LetterOrUnderscore
	: (Letter | '_') ;

fragment Letter
	: [A-Za-z] ;

VAR_START
	: '@' ;

STRING : [a-z]+;


// Whitespace and comments
//
LINE_TERMINATOR
	: [\n] -> skip ;

WHITESPACE
	: [ \t\r\u000C]+ -> skip ;

COMMENT
	: '/*' .*? '*/' -> skip ;

LINE_COMMENT
	: '//' ~[\r\n]* -> skip ;
