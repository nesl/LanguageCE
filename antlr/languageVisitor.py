# Generated from antlr/language.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .language import language
else:
    from language import language

# This class defines a complete generic visitor for a parse tree produced by language.

class languageVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by language#expr.
    def visitExpr(self, ctx:language.ExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by language#complexEvent.
    def visitComplexEvent(self, ctx:language.ComplexEventContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by language#atomicEvent.
    def visitAtomicEvent(self, ctx:language.AtomicEventContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by language#entityConstraint.
    def visitEntityConstraint(self, ctx:language.EntityConstraintContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by language#OverlapExpr.
    def visitOverlapExpr(self, ctx:language.OverlapExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by language#WithinExpr.
    def visitWithinExpr(self, ctx:language.WithinExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by language#bandInterval.
    def visitBandInterval(self, ctx:language.BandIntervalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by language#upperBoundInterval.
    def visitUpperBoundInterval(self, ctx:language.UpperBoundIntervalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by language#intervalParameter.
    def visitIntervalParameter(self, ctx:language.IntervalParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by language#timeIntervalParameter.
    def visitTimeIntervalParameter(self, ctx:language.TimeIntervalParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by language#spaceIntervalParameter.
    def visitSpaceIntervalParameter(self, ctx:language.SpaceIntervalParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by language#timeunit.
    def visitTimeunit(self, ctx:language.TimeunitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by language#spaceunit.
    def visitSpaceunit(self, ctx:language.SpaceunitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by language#relationOperator.
    def visitRelationOperator(self, ctx:language.RelationOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by language#entityProperty.
    def visitEntityProperty(self, ctx:language.EntityPropertyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by language#entity.
    def visitEntity(self, ctx:language.EntityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by language#propertyOptions.
    def visitPropertyOptions(self, ctx:language.PropertyOptionsContext):
        return self.visitChildren(ctx)



del language