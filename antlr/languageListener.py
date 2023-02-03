# Generated from antlr/language.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .language import language
else:
    from language import language

# This class defines a complete listener for a parse tree produced by language.
class languageListener(ParseTreeListener):

    # Enter a parse tree produced by language#expr.
    def enterExpr(self, ctx:language.ExprContext):
        pass

    # Exit a parse tree produced by language#expr.
    def exitExpr(self, ctx:language.ExprContext):
        pass


    # Enter a parse tree produced by language#complexEvent.
    def enterComplexEvent(self, ctx:language.ComplexEventContext):
        pass

    # Exit a parse tree produced by language#complexEvent.
    def exitComplexEvent(self, ctx:language.ComplexEventContext):
        pass


    # Enter a parse tree produced by language#atomicEvent.
    def enterAtomicEvent(self, ctx:language.AtomicEventContext):
        pass

    # Exit a parse tree produced by language#atomicEvent.
    def exitAtomicEvent(self, ctx:language.AtomicEventContext):
        pass


    # Enter a parse tree produced by language#entityConstraint.
    def enterEntityConstraint(self, ctx:language.EntityConstraintContext):
        pass

    # Exit a parse tree produced by language#entityConstraint.
    def exitEntityConstraint(self, ctx:language.EntityConstraintContext):
        pass


    # Enter a parse tree produced by language#OverlapExpr.
    def enterOverlapExpr(self, ctx:language.OverlapExprContext):
        pass

    # Exit a parse tree produced by language#OverlapExpr.
    def exitOverlapExpr(self, ctx:language.OverlapExprContext):
        pass


    # Enter a parse tree produced by language#WithinExpr.
    def enterWithinExpr(self, ctx:language.WithinExprContext):
        pass

    # Exit a parse tree produced by language#WithinExpr.
    def exitWithinExpr(self, ctx:language.WithinExprContext):
        pass


    # Enter a parse tree produced by language#operatorOptions.
    def enterOperatorOptions(self, ctx:language.OperatorOptionsContext):
        pass

    # Exit a parse tree produced by language#operatorOptions.
    def exitOperatorOptions(self, ctx:language.OperatorOptionsContext):
        pass


    # Enter a parse tree produced by language#bandInterval.
    def enterBandInterval(self, ctx:language.BandIntervalContext):
        pass

    # Exit a parse tree produced by language#bandInterval.
    def exitBandInterval(self, ctx:language.BandIntervalContext):
        pass


    # Enter a parse tree produced by language#upperBoundInterval.
    def enterUpperBoundInterval(self, ctx:language.UpperBoundIntervalContext):
        pass

    # Exit a parse tree produced by language#upperBoundInterval.
    def exitUpperBoundInterval(self, ctx:language.UpperBoundIntervalContext):
        pass


    # Enter a parse tree produced by language#intervalParameter.
    def enterIntervalParameter(self, ctx:language.IntervalParameterContext):
        pass

    # Exit a parse tree produced by language#intervalParameter.
    def exitIntervalParameter(self, ctx:language.IntervalParameterContext):
        pass


    # Enter a parse tree produced by language#timeIntervalParameter.
    def enterTimeIntervalParameter(self, ctx:language.TimeIntervalParameterContext):
        pass

    # Exit a parse tree produced by language#timeIntervalParameter.
    def exitTimeIntervalParameter(self, ctx:language.TimeIntervalParameterContext):
        pass


    # Enter a parse tree produced by language#spaceIntervalParameter.
    def enterSpaceIntervalParameter(self, ctx:language.SpaceIntervalParameterContext):
        pass

    # Exit a parse tree produced by language#spaceIntervalParameter.
    def exitSpaceIntervalParameter(self, ctx:language.SpaceIntervalParameterContext):
        pass


    # Enter a parse tree produced by language#timeunit.
    def enterTimeunit(self, ctx:language.TimeunitContext):
        pass

    # Exit a parse tree produced by language#timeunit.
    def exitTimeunit(self, ctx:language.TimeunitContext):
        pass


    # Enter a parse tree produced by language#spaceunit.
    def enterSpaceunit(self, ctx:language.SpaceunitContext):
        pass

    # Exit a parse tree produced by language#spaceunit.
    def exitSpaceunit(self, ctx:language.SpaceunitContext):
        pass


    # Enter a parse tree produced by language#relationOperator.
    def enterRelationOperator(self, ctx:language.RelationOperatorContext):
        pass

    # Exit a parse tree produced by language#relationOperator.
    def exitRelationOperator(self, ctx:language.RelationOperatorContext):
        pass


    # Enter a parse tree produced by language#entityProperty.
    def enterEntityProperty(self, ctx:language.EntityPropertyContext):
        pass

    # Exit a parse tree produced by language#entityProperty.
    def exitEntityProperty(self, ctx:language.EntityPropertyContext):
        pass


    # Enter a parse tree produced by language#entity.
    def enterEntity(self, ctx:language.EntityContext):
        pass

    # Exit a parse tree produced by language#entity.
    def exitEntity(self, ctx:language.EntityContext):
        pass


    # Enter a parse tree produced by language#propertyOptions.
    def enterPropertyOptions(self, ctx:language.PropertyOptionsContext):
        pass

    # Exit a parse tree produced by language#propertyOptions.
    def exitPropertyOptions(self, ctx:language.PropertyOptionsContext):
        pass


