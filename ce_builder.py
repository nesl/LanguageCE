#  This is our file for handling various objects and classes

import re
import traceback

def get_param_name(var):
    stack = traceback.extract_stack()
    filename, lineno, function_name, code = stack[-3]
    vars_name = re.compile(r'\((.*?)\).*$').search(code).groups()[0]
    print(vars_name)
    return




#  So, we have groups, objects, locations/watchboxes.
#   Each of them have functions/relations with other entities
#        which generate spatial events.
class video_stream:

    # Set up a video stream.
    def __init__(self, id):
        self.id = id

class watchbox:

    # Set up a watchbox
    def __init__(self, video_stream, positions):
        self.video_stream = video_stream
        self.positions = positions

class spatialEvent:

    # set up a spatialevent
    def __init__(self):

        self.event = {
            "value": True
        }


# This is an object group where most of our relations come into play
#  All that these relations do is return a dict of data and functions.
class obj_group:

    # Set up an object group with composition.
    def __init__(self, composition):
        self.composition = composition

    # Check if an object approaches a watchbox
    def approaches(self, watchbox, min_speed):
        #### TO BE IMPLEMENTED ####
        se = spatialEvent()
        return se

    # Check if an object enters a watchbox
    def enters(self, watchbox):
        #### TO BE IMPLEMENTED ####
        se = spatialEvent()
        return se

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


# See pytransitions "passing data"
class complexEvent:

    # Set up complex event
    def __init__(self):

        self.event = {
            "value": True
        }

        self.states = []
    
    # Now we need some traversal functions (e.g. get children, isleaf, etc)

def ce_and(event_list, time_constraints):
    return complexEvent()


def ce_until(event_list, time_constraints):
    return complexEvent()

def ce_follows(event_list):

    get_param_name(event_list)

    return complexEvent()



    