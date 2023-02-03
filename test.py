import torch
import json
import os

# Antlr stuff
from antlr4 import *
from antlr4.tree.Trees import Trees
from antlr.languageLexer import languageLexer  # This is the lexer 
from antlr.language import language   # This is the parser
from antlr.languageVisitor import languageVisitor  # This is the visitor
from nltk import Tree
from nltk.draw.tree import TreeView


class MyVisitor(languageVisitor):
    def visitNumberExpr(self, ctx):
        value = ctx.getText()
        return int(value)

    def visitParenExpr(self, ctx):
        return self.visit(ctx.expr())

    def visitInfixExpr(self, ctx):
        l = self.visit(ctx.left)
        r = self.visit(ctx.right)

        op = ctx.op.text
        operation =  {
        '+': lambda: l + r,
        '-': lambda: l - r,
        '*': lambda: l * r,
        '/': lambda: l / r,
        }
        return operation.get(op, lambda: None)()

    def visitWithinExpr(self, ctx):
        print("Enter Within")

    def visitHelloExpr(self, ctx):
        return ("hi")


def pretty_print(treestring):

    indents = treestring.split("(")

    p1 = treestring.count("(")
    p2 = treestring.count(")")

    print(p1)
    print(p2)

    # num_indents = 0
    # for x in indents:
    #     indent_string = '\t'*num_indents
    #
    #     print(indent_string + x)
    #
    #     if ")" in x:
    #         num_indents -= 1
    #     else:
    #         num_indents += 1

    # s = printtree + "\\"
    # s = printtree.replace(')', '\)').replace('(', '\(') # fix
    # print(treestring)
    nltk_tree = Tree.fromstring(treestring)

    TreeView(nltk_tree)._cframe.print_to_file('output.ps')
    os.system('convert output.ps output.png')


def perform_inference():

    # Model
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=False)
    model.load_state_dict(torch.load('multiV1_weights.pt'))['model'].state_dict()

    # Images
    imgs = ['output/image272.png']  # batch of images

    # Inference
    results = model(imgs)

    # Results
    results.print()


# Apply labelme to necessary locations
def label_locations(entity_locations):

    entity_location_names = list(entity_locations.keys())

    # For each entity location name, check if there's actually a file for it
    for entity_location_name in entity_location_names:

        # If this file doesn't exist, then call the labelme
        if not os.path.exists(entity_locations[entity_location_name]["file"]):
            
            os.system("labelme example.png")

        


# Obtain all the entities involved in the event
def obtain_event_entities(event_str, entities):


    # First, check the locations and label them if necessary
    label_locations(entities["locations"])

    entity_dict = {}
    entity_dict.update(entities["objects"])
    entity_dict.update(entities["locations"])
    entity_dict.update(entities["groups"])

    

    # Split all parts of the event_str
    # event_parts = event_str.split()



# Parse the query
def parse_query(filepath="example.json"):

    f = open(filepath)
    data = json.load(f)
    f.close()

    # Get all the entities
    entities = data["entities"]
    # Get the event
    event = data["event"]
    # Get all entities involved in the event
    # event_entities = obtain_event_entities(event, entities)

    # lexer
    # "within[1KM](@rec_vehicle , @bridge1_watchbox)"
    # "@rec_vehicle . type == 5"
    # overlap(@rec_group, @bridge_watchbox1) and[1m] overlap(@rec_group, @bridge_watchbox2)
    input_text = InputStream("overlap(@rec_group, @bridge_watchbox1) and[1m] overlap(@rec_group, @bridge_watchbox2)")
    lexer = languageLexer(input_text)
    stream = CommonTokenStream(lexer)
    # parser
    parser = language(stream)
    tree = parser.expr()

    # Print tree
    printtree = Trees.toStringTree(tree, None, parser)
    # printtree = "(" + printtree

    print(printtree)

    pretty_print(printtree)


    # evaluator
    visitor = MyVisitor()
    output = visitor.visit(tree)
    print(output)



parse_query()