# Script for lexing/parsing our grammar

source venv/bin/activate
antlr4 -Dlanguage=Python3 antlr/languageLexer.g4 
antlr4 -visitor -Dlanguage=Python3 antlr/language.g4 
python test.py