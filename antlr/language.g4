parser grammar language;

options {
	tokenVocab = languageLexer ;
}

/*
 *   Parser Rules
 */

expr:
    customEvent ;


customEvent
    : STRING 
    ;

/*  This is for EVENT EQUALITY_OPERATOR VALUE */
constraintEvent
    : 
    ;




atomicEvent
    : NotOperator? entityConstraint
    | NotOperator? spatialEvent ;


entityConstraint
    : entityProperty relationOperator IntegerLiteral;

spatialEvent
    :  OverlapOperator LPAREN entity COMMA entity RPAREN #OverlapExpr
    |  WithinOperator upperBoundInterval LPAREN entity COMMA entity RPAREN #WithinExpr
    ;  


operatorOptions
    : bandInterval | upperBoundInterval ;

bandInterval
  	: LBRACK intervalParameter ( COLON | COMMA ) intervalParameter RBRACK ;

upperBoundInterval
    : LBRACK intervalParameter RBRACK ;


intervalParameter:
    timeIntervalParameter
    | spaceIntervalParameter ;

timeIntervalParameter
	: IntegerLiteral ( timeunit )? 
	| Identifier ( timeunit )? 
  | Infinity  ; 


spaceIntervalParameter
    : IntegerLiteral ( spaceunit )? ;


timeunit
      : SEC | MSEC | USEC | NSEC ;

spaceunit
    : MILES | KILOMETERS;


relationOperator
    : EqualOperator | NotEqualOperator | GreaterOrEqualOperator | LesserOrEqualOperator | GreaterOperator | LesserOperator ;




entityProperty
    : entity DOT propertyOptions ;

entity
    : VAR_START STRING;

propertyOptions
    : EntityType | EntityLocation | GroupMemberDistances | GroupPositions | propertyOptions DOT propertyOptions ;