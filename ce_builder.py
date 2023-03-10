#  This is our file for handling various objects and classes

import re
import traceback
from transitions import Machine
from transitions.extensions import HierarchicalMachine
from transitions.extensions import GraphMachine
from transitions.extensions.factory import HierarchicalGraphMachine
import json

from antlr4 import *
from antlr4.tree.Trees import Trees
from antlr.languageLexer import languageLexer  # This is the lexer 
from antlr.language import language   # This is the parser


import os, sys, inspect, io
from IPython.display import Image, display, display_png


# Always recompile the ANTLR language
# os.system("bash run_test.sh")


def get_param_name(var):
    stack = traceback.extract_stack()
    filename, lineno, function_name, code = stack[-3]
    vars_name = re.compile(r'\((.*?)\).*$').search(code).groups()[0]
    return vars_name


# This is the event class
class spatialEvent:

    set_of_logical_operators = [" and ", " or "]
    set_of_equality_operators = [">=", "==", "<=", "<", ">"]

    # This has to return a set of states (for this event)
    #   as well as a function for updating those states.
    # def parse_event_function(self, event_function):


    # Get entities
    def get_entities(self, event_function):

        print(event_function)
        entities = []
        # Every entity will have a period following it.
        for candidate in event_function.split(".")[:-1]:
            entity = candidate.split(" ")[-1]
            entities.append(entity)
            
        return entities

    # set up a spatialevent
    def __init__(self, event_name, event_function, complete_code_block):

        # self.states = states
        # self.transitions = transitions

        self.event_name = event_name
        self.event_function = event_function
        self.modified_event_function = event_function

        # We need to execute the code block, which will give us the variables we need.
        exec(complete_code_block)

        # Now, we have a parsing function which gives us a set of 
        #  states that we can update
        entities = self.get_entities(event_function)

        self.objects = []
        for i,entity_var_name in enumerate(entities):
            exec("self.objects.append(" + entity_var_name + ")")
            
            self.modified_event_function = \
                    self.modified_event_function.replace(entity_var_name+".", "self.objects[" + str(i) + "]"+".")

    # Evaluate our states
    def evaluate(self):
        return eval(self.modified_event_function)


    def update(self, data):
        for x in self.objects:
            x.update(data)
        
    


#  This has to return a lambda function that we can evaluate over later
def event_compile(param):

    (filename,line_number,function_name,text)=traceback.extract_stack()[-2]
    event_call_text = text
    
    event_name = text.split("event_compile")[1][1:-1]
    event_call_line = line_number-1  # Index not starting from zero
    
    # So we find the event name, and figure out what the text was saying.
    f = open("LanguageTest.ipynb", "r")
    python_code = json.load(f)
    f.close()

    # Now we have to find the 'closest previous' instantiation of this event
    complete_code_block = None
    relevant_line = None
    relevant_line_found = False
    for cell in python_code["cells"]:

        # First, check if this is the relevant cell or line
        if len(cell["source"]) >= event_call_line and \
                event_call_text in cell["source"][event_call_line]:
            relevant_line_found = True

        # Remember this code block - it will be useful later.
        complete_code_block = ''.join(cell["source"][:event_call_line])

        if relevant_line_found:
            # Look in reverse from the point of this event being called.
            for line in cell["source"][event_call_line-1::-1]:
                # If the event name is found, remember this line
                if event_name in line:
                    relevant_line = line.strip()
                    cutoff_index = relevant_line.find("=")+1
                    relevant_line = relevant_line[cutoff_index:].strip()
                    break
        
        if relevant_line:
            break

    # Upon getting the relevant line, we have to parse it.
    #  There are a few common patterns -
    #  function EQUALITY VALUE
    #  function EQUALITY VALUE LOGICAL_VALUE function EQUALITY VALUE
    return spatialEvent(event_name, relevant_line, complete_code_block)


#  So, we have groups, objects, locations/watchboxes.
#   Each of them have functions/relations with other entities
#        which generate spatial events.
class sensor_event_stream:

    # Set up a video stream.
    def __init__(self, id):
        self.id = id

class watchbox:

    # Set up a watchbox
    def __init__(self, video_stream, positions):
        self.video_stream = video_stream
        self.positions = positions
        self.data = []

    # Returns composition at a particular time
    #  This looks backwards in data
    def composition(self, at, model):

        if self.data:
            # Get the data at a timestamp
            #  0 is -1, 1 is -2, etc.
            composition_result = self.data[-at - 1]
            return composition_result

    # Updates some internal values
    def update(self, data):
        self.data.append(data)
    
        




# This is an object group where most of our relations come into play
#  All that these relations do is return a dict of data and functions.
class obj_group:

    # Set up an object group with composition.
    def __init__(self, composition):
        self.composition = composition

        # Get the variable name of the class instance.
        (filename,line_number,function_name,text)=traceback.extract_stack()[-2]
        self.obj_group_name = text[:text.find('=')].strip()



    # Check if an object approaches a watchbox
    def approaches(self, watchbox, min_speed):
        #### TO BE IMPLEMENTED ####
        se = spatialEvent()
        return se

    # Check if an object enters a watchbox
    def enters(self, watchbox):

        watchbox_name = get_param_name(watchbox)
        
        state_prefix = self.obj_group_name
        state_suffix = watchbox_name

        # There are two transitions and states - enters and exits
        states = [
            state_prefix + '-present-' + state_suffix,
            state_prefix + '-gone-' + state_suffix
        ]
        transitions = [
            {"trigger": state_prefix + '-entered-' + state_suffix,
                "source": state_prefix + '-gone-' + state_suffix,
                "dest": state_prefix + '-present-' + state_suffix },
            {"trigger": state_prefix + '-exited-' + state_suffix,
                "source": state_prefix + '-present-' + state_suffix,
                "dest": state_prefix + '-gone-' + state_suffix }
        ]

        #  Construct a spatial event from this
        return spatialEvent(states, transitions)

    # Check if an object enters a watchbox
    def exits(self, watchbox):
        #### TO BE IMPLEMENTED ####
        se = spatialEvent()
        return se

    # # This returns a constraint
    # def create_subgroup(self, num_members):
    #     new_composition = self.composition
    #     new_obj_group = obj_group()
    #     return se


#  There are also temporal events which are more general and don't fall under
#   those relations. 
#  The "ComplexEvent" class also has methods for compiling, visualizing,
#    and executing.


# So our CEs will need a few things:
#  First is obviously enumeration of states, such that they can be hierarchical
#   Of course, then we have the initial state.
#  Then we add our transitions, which can run functions before/after the transition.
#    Each transition needs a function trigger...

class Model:
    def clear_state(self, deep=False, force=False):
        print("Clearing state ...")
        return True

# See pytransitions "passing data"
class complexEvent:

    # Set up complex event
    def __init__(self, states, transitions, event_name):
        self.states = states
        self.transitions = transitions
        self.ce_name = event_name
        
        self.machine = None

    # Add the compilation
    def compile(self):

        # Basically, we construct our machine from the states and transitions
        self.machine = HierarchicalMachine(model=self, states=self.states, \
                transitions=self.transitions, initial='asleep')

        # We need to add a transition for going from 'asleep' to our first state.
        

    # Add the visualization
    def visualize(self):

        m = Model()
        # without further arguments pygraphviz will be used
        machine = HierarchicalGraphMachine(model=m, states=self.states, \
                transitions=self.transitions, initial='asleep')
        # draw the whole graph ...
        m.get_graph().draw('my_state_diagram.png', prog='dot')

    # Now we need some traversal functions (e.g. get children, isleaf, etc)


def ce_and(event_list, time_constraints):

    (filename,line_number,function_name,text)=traceback.extract_stack()[-2]
    ce_name = text[:text.find('=')].strip()

    # Name the current state
    #  Either "AND" is satisfied or it is not.

    sub_states = []
    sub_transitions = []
    for event in event_list:
        sub_states.extend(event.states)
        sub_transitions.extend(event.transitions)

    states = [
        {'name': ce_name + '-true-', 'children':sub_states},
        {'name': ce_name + '-false-', 'children':sub_states},
    ]
    transitions = [
        {"trigger": ce_name + '-and',
            "source": ce_name + '-false',
            "dest": ce_name + '-true' },
        {"trigger": ce_name + '-notand',
            "source": ce_name + '-true',
            "dest": ce_name + '-false' }
    ]
    transitions.extend(sub_transitions)


    return complexEvent(states, transitions, ce_name)


def ce_until(event_list, time_constraints):


    return

def ce_follows(event_list):

    event_name = get_param_name(event_list)

    return



# The first thing we need to do is to be able to construct a tree of 
#  the functions and their order of execution.  This means constructing
#   a list of states (ALL STATES.)