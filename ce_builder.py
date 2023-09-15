#  This is our file for handling various objects and classes

import re
import traceback
import itertools
import os, sys, inspect, io
from utils import parse_ae
import cv2
import numpy as np


def get_param_name(var):
    stack = traceback.extract_stack()
    filename, lineno, function_name, code = stack[-3]
    vars_name = re.compile(r'\((.*?)\).*$').search(code).groups()[0]
    return vars_name

#  So, we have groups, objects, locations/watchboxes.
#   Each of them have functions/relations with other entities
#        which generate spatial events.
class sensor_event_stream:

    # Set up a video stream.
    def __init__(self, id):
        self.id = id


class watchboxResult:

    def __init__(self, time=0, obj_event={}, previous_state={}, locations={}):

        # Blank state
        if not obj_event and not previous_state:
            self.objects = {}
            self.locations = {}
            self.size = 0
            self.speed = 0
            self.color = ""
            self.time = 0
            return
        
        # Otherwise, just proceed as before.
        self.objects = self.get_new_states(obj_event, previous_state)
        self.locations = locations
        # Now we can calculate these items
        self.size = len(self.objects.keys())
        self.speed = 0
        self.color = ""
        self.time = time

    # Directly set states
    def directly_set_states(self, time, objects, locations):
        self.objects = objects
        self.locations = locations
        self.size = len(self.objects.keys())
        self.time = time

    # Get an updated state
    def get_new_states(self, obj_event, previous_state):
        
        new_objects = previous_state.objects.copy()

        # Check if a new object enters or an old one leaves
        track_id = obj_event["track_id"]
        
        if obj_event["enters"]:  # Object is entering
            new_objects[track_id] = obj_event
        else:  # Object is leaving
            if track_id in new_objects:
                new_objects.pop(track_id)

        return new_objects
    
    def get_as_dict(self):
        dict_result = {"time": self.time, "objects": self.objects}
        return dict_result


        
class watchbox:

    # Set up a watchbox
    def __init__(self, camera_id, positions, classes, watchbox_id, class_mappings):
        self.camera_id = int(camera_id)
        self.positions = positions
        self.watchbox_id = watchbox_id
        self.classes = classes
        self.class_mappings = class_mappings
        self.data = [watchboxResult()]
        self.max_history = 1000
        
    # update the max history
    def updateMaxHistory(self, history_len):
        if self.max_history < history_len:
            self.max_history = history_len
        
    # Returns composition at a particular time
    #  This looks backwards in data
    def composition(self, at, model):

        if self.data:
            # Get the data at a timestamp
            #  0 is -1, 1 is -2, etc.
            
            # We take either the smallest value or the at value
            at_key = max(-len(self.data), -at - 1)

            composition_result = self.data[at_key]

            # Make sure you only get the composition for the relevant object
            if model:
                # Go to class mappings
                class_index = self.class_mappings[model]

                time = composition_result.time

                # Get all objects with match class index
                related_objects = {}
                for key in composition_result.objects.keys():
                    if class_index == composition_result.objects[key]['class']:
                        related_objects[key] = composition_result.objects[key]
                composition_result = watchboxResult()
                composition_result.objects = related_objects
                composition_result.time = time
                composition_result.size = len(related_objects.keys())
            
            return composition_result
        
    

    # Updates some internal values
    #  Data looks like: 
    #  {'camera_id': camera_id, 'results': {'track_id': 36, 'watchboxes': 
    #      [0], 'enters': [True], 'directions': ['middle']} }
    def update(self, data, tracks, frame_index):
        
        # Remember - we are updating a list of dictionaries

        # Get the camera id and results
        incoming_cam_id = data["camera_id"]
        results = data["results"]

        # Get the relevant matching watchbox
        for c_i, current_wb_id in enumerate(results["watchboxes"]):
            # Make sure the wb id matches and the camera id matches
            if self.watchbox_id == current_wb_id and self.camera_id == int(incoming_cam_id): # watchbox id matches and same with the camera id

                # print("Updating for watchbox ID" + str(self.watchbox_id) + " and cam " + str(self.camera_id))
                
                # Get the new object event
                obj_event = {"track_id": results["track_id"], 
                            "enters": results["enters"][c_i], 
                            "directions": results["directions"][c_i],
                            "class": results["class"]}
                # Get relevant watchboxes
                locations = tracks[results["track_id"]]["bbox_data"]
            
                # Append to our data
                self.data.append(watchboxResult(frame_index, obj_event, self.data[-1], locations))

                # Also make sure our max_history_length is being enforced
                while len(self.data) > self.max_history+1: # +1 because current timestamp is included
                    self.data.pop(0)


class Model:
    def clear_state(self, deep=False, force=False):
        print("Clearing state ...")
        return True
    
class OR:
    def __init__(self, *args):
        # Basically needs to return the full string but and/or
        # output = ' or '.join(["("+x.event+")" for x in args])
        
        output = [x.event for x in args]
        output.append("or")
        self.event = output
        self.event_name = [x.event_name for x in args]

            
class AND:
    def __init__(self, *args):
        # Basically needs to return the full string but and/or
        # output = ' and '.join(["("+x.event+")" for x in args])
        output = [x.event for x in args]
        output.append("and")
        self.event = output
        self.event_name = [x.event_name for x in args]
        

class NOT:
    # Mainly deals with 
    #  not AND
    #  not OR
    #  not atomic event
    def __init__(self, *args):
    
        # First, identify any keywords
        output = args[0].event

        # Check if we are using AND or OR
        if len(output) > 1:
            operator = output[-1]
            output[-1] = "not " + operator
            self.event_name = args[0].event_name
        else: # Then we are just NOT-ing a regular AE
            output = [output, "not"]
            self.event_name = [args[0].event_name]

        self.event = output

class SET:
    def __init__(self, *args):
        
        # First, get the time parameter and ignore the rest
        
        # generate the statement to execute
        output = [[x.event[0]] for x in args]
        output.append(["set_untimed"])

        self.event = output
        self.event_name = [x.event_name for x in args]

class SEQUENCE:
    def __init__(self, *args):
        
        # First, get the time parameter and ignore the rest
        
        # generate the statement to execute
        new_statements = []
        for x in args:
            if type(x) == list:
                new_statements.extend(x)
            else:
                new_statements.append(x)

        output = [[x.event[0]] for x in new_statements]
        output.append(["sequence_untimed"])

        self.event = output
        self.event_name = [x.event_name for x in new_statements]


class SET_TIMED:
    # Initializing a WITHIN statement is a bit tricky, as it refers to checking when
    #  an event becomes true within a certain amount of time.
    #  So it also requires an additional statement that checks if one time from one event is within another
    def __init__(self, *args):
        
        # First, get the time parameter and ignore the rest
        time_param = args[-1]
        statements = args[:-1]

        new_statements = []
        for x in statements:
            if type(x) == list:
                new_statements.extend(x)
            else:
                new_statements.append(x)
        
        # generate the statement to execute
        output = [[x.event[0]] for x in new_statements]
        output.append(["set_timed", None, time_param])

        self.event = output
        self.event_name = [x.event_name for x in new_statements]


class SEQUENCE_TIMED:
    # Initializing a WITHIN statement is a bit tricky, as it refers to checking when
    #  an event becomes true within a certain amount of time.
    #  So it also requires an additional statement that checks if one time from one event is within another
    def __init__(self, *args):
        
        # First, get the time parameter and ignore the rest
        time_param = args[-1]
        statements = args[:-1]
        
        # generate the statement to execute
        # Go through each element of the statements, and un-listify it
        new_statements = []
        for x in statements:
            if type(x) == list:
                new_statements.extend(x)
            else:
                new_statements.append(x)

        output = [[x.event[0]] for x in new_statements]
        output.append(["sequence_timed", None, time_param])

        self.event = output
        self.event_name = [x.event_name for x in new_statements]

class HOLDS:

    def __init__(self, *args):

        # First, identify any keywords
        time_param = args[-1]
        statements = args[:-1]
         # generate the statement to execute
        output = [[x.event[0]] for x in statements]
        output.append(["holds", None, time_param])

        self.event = output
        self.event_name = [x.event_name for x in statements]
        
# So how should this function work?
#  Firstly, it must be able to expand the maximum history -
#   e.g. at=1 size==2 and at=0 size==0
#       should have another option: at=2 size==2 and at=1 size==1 and at=0 size==0
#  So it's really a matter of 'filling out the middle'.
class GEN_PERMUTE:
    
    def get_attributes(self, statement, attribute):
        
        # First, get the time
        time = statement.split("at=")[1].split(",")[0]
        # Then, get the attribute value
        attr_value = statement.split(attribute)[1][2:]
        
        return (int(time), int(attr_value))
    
    # Now, we must generate permutations
    #  We must generate all possible permutations between these values
    def gen_combinations(self, attribute_values, times):
        
        # First, we must note the order: Is time increasing?  Are the attribute values increasing?
        time_ascending = times[0] < times[1]
        min_time = min(times)
        attributes_ascending = attribute_values[0] < attribute_values[1]
        
        # Next, figure out all subsets of those attribute values
        smallest_attribute_value = min(attribute_values)
        largest_attribute_value = max(attribute_values)
        # First, get all possible values (e.g. treat attribute_values as a range)
        new_possible_values = [i for i in range(smallest_attribute_value, largest_attribute_value+1)]
        
        possible_combinations = []
        # Now, get all possible combos which contain both values
        for L in range(len(new_possible_values) + 1):
            for subset in itertools.combinations(new_possible_values, L):
                # Make sure we have both values in it
                if smallest_attribute_value in subset and largest_attribute_value in subset:
                    possible_combinations.append(list(subset))
        
        # Now, we have to make sure our times and our attributes follow the same order
        #  as when we had read them in
        results = []
        for combo in possible_combinations:
            # Generate the time in order
            current_times = [x for x in range(min_time, min_time+len(combo))]
            if not time_ascending:
                current_times.sort(reverse=True)
            
            # Generate the combinations in order
            combo.sort()
            if not attributes_ascending:
                combo.sort(reverse=True)
                
            results.append((current_times, combo))
        
        return results
        
    # Note - combos is like ([list of times],[list of attribute values])
    def generate_statement_from_combo(self, combo, attribute, statement):
        
        # Get the text of the time that we should replace
        original_time_statement = "at="+statement.split("at=")[1].split(",")[0]
        original_attribute_statement = attribute + statement.split(attribute)[1]
        
        # Now, get the starting statements
        starting_statement_time = "at="
        starting_statement_attr = ''.join([x for x in original_attribute_statement if not x.isdigit()])
        
        # And now replace with the combo values
        times = combo[0]
        att_values = combo[1]
        completed_statement = []
        for i in range(len(times)):
            replacing_time_statement = starting_statement_time + str(times[i])
            replacing_att_statement = starting_statement_attr + str(att_values[i])
            
            # Here we replace our values with the new ones
            modified_statement = statement.replace(original_time_statement, replacing_time_statement)
            modified_statement = modified_statement.replace(original_attribute_statement, \
                                                                replacing_att_statement)
            completed_statement.append(modified_statement)
            
        completed_statement = " and ".join(completed_statement)
        
        return completed_statement
        
    
    def __init__(self, event, attribute):
        
        # First, we should determine what the possible transitions are between 
        #  the values involved with the attributes
        split_statements = event.event[0].replace("and", "--")
        split_statements = split_statements.replace("or", "--")
        split_statements = [x.strip() for x in split_statements.split("--")]
        
        times = []
        attribute_values = []
        for statement in split_statements:
            # Now, iterate through each statement and get its time and attribute value
            time, attr_value = self.get_attributes(statement, attribute)
            times.append(time)
            attribute_values.append(attr_value)
            
        time_attr_combos = self.gen_combinations(attribute_values, times)
        
        combination_statements = []
        # Now, we must iterate through every combination and create the equivalent statement
        for combo in time_attr_combos:
            completed_statement = \
                self.generate_statement_from_combo(combo, attribute, split_statements[0])
            combination_statements.append("("+completed_statement+")")
            
        combo_statement = ' or '.join(combination_statements)
        self.event = [combo_statement]
        self.event_name = event.event_name

class Event:
    
    def __init__(self, event_str):
        (filename,line_number,function_name,text)=traceback.extract_stack()[-2]
        event_call_text = text.split("=")[0]
        self.event_name = event_call_text
        self.event = [event_str]
    
class complexEvent:

    # Set up complex event
    def __init__(self, class_mappings):
          
        (filename,line_number,function_name,text)=traceback.extract_stack()[-2]
        event_call_text = text.split("=")[0]
        self.event_name = event_call_text
        
        
        self.watchboxes = {}
        self.config_watchboxes = {}
        self.class_mappings = class_mappings
        self.client_info = {}
        self.executable_functions = []  # This is a list of [func_name, function]
        # This stores the previous state of each event initially
        self.previous_eval_result = {}  
        self.current_index = 0

        self.within_history = {} # Keep track of events which must occur in a particular time constraint
        self.holds_history = {} # Keep track of atomic events which are being held in time
        
        # Keep track of our json output
        self.result_output = {"incoming":[], "events":[]}
        self.result_dir = ""
    
    # Set up our result directory
    def set_result_dir(self, result_dir):
        if not os.path.exists(result_dir):
            os.mkdir(result_dir)
        self.result_dir = result_dir
        
        
    # Add watchboxes
    def addWatchbox(self, name, region_id, positions, classes, watchbox_id, class_mappings):

        current_watchbox = watchbox(region_id, positions, classes, watchbox_id, class_mappings)
        current_data = [name, current_watchbox]

        self.watchboxes.update({current_data[0]:current_data[1]})


    # Generate watchbox data to send
    def getWatchboxConfigs(self):

        #  Should look like { cam_id: [[positions, [classes]], []...]}
        watchbox_config = {}
        # Iterate through every watchbox
        for wb_key in self.watchboxes.keys():
            current_watchbox = self.watchboxes[wb_key]
            # Get the properties
            cam_id = current_watchbox.camera_id
            wb_positions = current_watchbox.positions
            wb_classes = current_watchbox.classes
            wb_id = current_watchbox.watchbox_id

            for class_id in wb_classes:

                # First, get the class ID as an integer
                class_index = self.class_mappings[class_id]

                if cam_id not in watchbox_config:
                    watchbox_config[cam_id] = [wb_positions+[class_index,wb_id]]
                else:
                    watchbox_config[cam_id].append(wb_positions+[class_index,wb_id])
        
        return watchbox_config
        

        
    # Iterate through every watchbox name, and replace it with the object reference
    def replaceWatchboxCommands(self, event):
        
        new_commands = []

        # Iterate through every 'event'
        #  ev could be an event string, or it could be a list of event strings
        for ev in event:
            
            if type(ev) == str:
                ev = [ev]

            sub_new_commands = []

            # Itereate through sub ev
            for sub_ev in ev:
                new_command = sub_ev

                for wb in self.watchboxes.keys():
                    # If the watchbox name matches, replace the command with the string
                    if wb in new_command:
                        new_wb_object = "self.watchboxes[\""+wb+"\"]"
                        new_command = new_command.replace(wb, new_wb_object)
                
                # Append after making these changes
                sub_new_commands.append(new_command)
            
            new_commands.append(sub_new_commands)
        
        return new_commands
    
    # Figure out how much 'history' each object needs to recall
    def updateMaxHistory(self, function_to_execute):


        if type(function_to_execute) == list:
            function_to_execute = function_to_execute[0][0]
        
        
        # Get every watchbox involved, and their 'time' for looking back
        # Split by and/or
        watchbox_statements = function_to_execute.replace("and", "--")
        watchbox_statements = watchbox_statements.replace("or", "--")
        # Now split by the delimiter --
        split_statements = watchbox_statements.split("--")
        # Now iterate through each watchbox statement and figure out its history
        for x in split_statements:
            # Get the name of the watchbox
            name = x.split("[\"")[1].split("\"]")[0]
            history_len = int(x.split("at=")[1].split(",")[0])
            # Update the max history (checking of 'max' is done at the watchbox side)


    # For a sequence of split event names, make sure to actually connect the OR/AND events back together
    #  e.g. given ["OR(ev11a", " ev11b)"] turn it into ["OR(ev11a, ev11b)"]
    def connectOperatorEvents(self, split_sequence):
        buffer = []
        output = []
        start_buffer = False
        using_gen_permute = False
        skip_next_item = False
        for x in split_sequence:
            
            if "(" in x:
                
                if "GEN_PERMUTE" in x:
                    using_gen_permute = True
                
                start_buffer = True
                x = x.split("(")[1]
                
                
                
            elif ")" in x:
                start_buffer = False
                x = x.split(")")[0]
                
                if using_gen_permute:
                    using_gen_permute = False
                    skip_next_item = True
                
            else:
                start_buffer = False
            

            if not skip_next_item:
                buffer.append(x)
            skip_next_item = False

            if not start_buffer:
                output.append(','.join(buffer))
                buffer = []

        return output
            

    # This replaces the watchbox names with our own CE watchbox objects
    def recurse_replace(self, event_tup):
    
        event_name = event_tup[0]
        event = event_tup[1]

        # If this is a string, then we have reached an AE
        if len(event) == 1:  # Only one element means we only have one event involving a watchbox
            # Get the function with a swapped name of our watchbox
            current_function = self.replaceWatchboxCommands([event])
            current_function = current_function[0][0]
            

            self.within_history[event_name] = []
            self.previous_eval_result[event_name] = [False, 0]
            return (event_name, current_function)
                
        else:  #If this is a list, then we go through each item except the last
            function_to_execute = []
            for e_i, sub_event in enumerate(event[:-1]):
                out = self.recurse_replace((event_name[e_i], sub_event))
                function_to_execute.append(out)
            function_to_execute.append(event[-1])
            return function_to_execute
    
    
    # Add sequence of events
    # This initializes self.executable_functions to a particular format:
    #  [ 
    #    (   [ eventname, event_logic ] , event_operator ), ([eventname, event_logic], ...) ...
    #  ]
    # It also initializes self.previous_eval_result to a particular format:
    #  {
    #    eventname : [boolean state, number of times state became true]
    #  }
    def addEvents(self, events):# , no_enforce_sequence=False):
    
        # self.no_enforce_sequence = no_enforce_sequence
        
        # Iterate through each event
        for event in events:

            # Deal with some bracketing errors
            to_send = None
            single_ae = False
            if type(event.event[0]) == str:   # This means it's a single-AE
                single_ae = True
            to_send = (event.event_name, event.event)  # This means it's a multi AE

            # Get the a list of [(func_name, code), (func_name, code), ..., operator]
            function_to_execute = self.recurse_replace(to_send)
            if single_ae:
            	function_to_execute = [function_to_execute]

            self.executable_functions.append(function_to_execute)
        

        # Also, finalize the watchbox data we are going to send
        self.config_watchboxes = self.getWatchboxConfigs()

      
    # Add update and evaluate
    def update(self, data, tracks, time_index):
        
        # Data will take on a structure like:
        # [{'camera_id': 0, 'results': [{'track_id': 36, 'watchboxes': [0], 
        #        'enters': [True], 'directions': ['middle']}], 'time': 2067}]

        camera_id = data[0]["camera_id"]
        result_list = data[0]["results"]

        # Iterate through the results for this camera
        for result in result_list:

            # Create a new result item for updating watchboxes
            update_data = {'camera_id': camera_id, 'results': result}

            # Update each watchbox
            for x in self.watchboxes.keys():
                self.watchboxes[x].update(update_data, tracks, time_index)


    # Get occurrence times
    def get_occurrence_timed(self, event_names, eval_results, time_index):

        within_occurrence_times = {}  # Get times
        for ev_i, ev_name in enumerate(event_names):
            if ev_name not in self.within_history:
                self.within_history[ev_name] = []

            # This event occurred
            if eval_results[ev_i] and not self.within_history[ev_name]:
                self.within_history[ev_name].append(time_index)
            
            if self.within_history[ev_name]:  # Get the times for the relevant events
                within_occurrence_times[ev_name] = self.within_history[ev_name][0]
        
        return within_occurrence_times

    
    def set_untimed(self, event_names, eval_results, time_index):
        result = False
        occurrence_times = self.get_occurrence_timed(event_names, eval_results, time_index)
        
        # This means all events have occurred
        if len(occurrence_times.keys()) == len(event_names):
            result = True

        return result
    
    def sequence_untimed(self, event_names, eval_results, time_index):
        result = False
        occurrence_times = self.get_occurrence_timed(event_names, eval_results, time_index)
        
        # This means all events have occurred
        if len(occurrence_times.keys()) == len(event_names):
            # Now check if all occur in time
            in_order = True
            prev_time = 0
            for ev_name in event_names:
                if occurrence_times[ev_name] <= prev_time:
                    in_order = False
                    break
                prev_time = occurrence_times[ev_name]

            #  All events occur in order and all events occur
            if in_order:
                result = True

        return result
    

    def sequence_timed(self, event_names, eval_results, placeholder, time_bound, time_index):
        
        result = False
        within_occurrence_times = self.get_occurrence_timed(event_names, eval_results, time_index)
        
        # Check if within occurred
        if len(within_occurrence_times.keys()) == len(event_names):
            # Now check if all occur in time
            in_order = True
            prev_time = 0
            for ev_name in event_names:
                if within_occurrence_times[ev_name] <= prev_time:
                    in_order = False
                    break
                prev_time = within_occurrence_times[ev_name]

            # Now check if the differences in times are correct
            max_time = max(within_occurrence_times.values())
            min_time = min(within_occurrence_times.values())

            if in_order and (max_time - min_time) < time_bound:
                result = True

        return result
            
    def set_timed(self, event_names, eval_results, placeholder, time_bound, time_index):
    
        result = False
        within_occurrence_times = self.get_occurrence_timed(event_names, eval_results, time_index)
        
        # Check if within occurred
        if len(within_occurrence_times.keys()) == len(event_names):

            # Now check if the differences in times are correct
            max_time = max(within_occurrence_times.values())
            min_time = min(within_occurrence_times.values())

            if (max_time - min_time) < time_bound:
                result = True

        return result

        # Get occurrence times
    def get_occurrence_holds(self, event_names, eval_results, time_index):

        within_occurrence_times = {}  # Get times
        for ev_i, ev_name in enumerate(event_names):
            if ev_name not in self.holds_history:
                self.holds_history[ev_name] = []

            # This event occurred and has not been mentioned before
            if eval_results[ev_i] and not self.holds_history[ev_name]:
                self.holds_history[ev_name].append(time_index)

            # This event became false after it occurring previously
            if not eval_results[ev_i] and self.holds_history[ev_name]:
                within_occurrence_times[ev_name] = self.holds_history[ev_name][0]
                self.holds_history[ev_name] = []
                
        return within_occurrence_times

    #  Check if an event holds for a length of time
    def holds(self, event_names, eval_results, placeholder, time_bound, time_index):

        result = False
        within_occurrence_times = self.get_occurrence_holds(event_names, eval_results, time_index)

        # Check if this event has occurred for a particular amount of time
        if len(within_occurrence_times.keys()) == len(event_names):
            max_time = max(within_occurrence_times.values())
            if (time_index - max_time) >= time_bound:
                result = True
        
        return result
            

    # Get the actual function we need to evaluate
    def get_func_to_evaluate(self, func_list, func_name, time_index):

        output = ""
        func_list = func_list[0] # Get rid of extra list
        if len(func_list) == 1:
            output = func_list[0]
        else:  # If we have multiple things to check, then it's likely we have an operator here.
            # Iterate through each function

            # If this is a within, then create the appropriate function name
            if func_list[-1][0] == "within":
                params = [str(func_list[0:-1]), "\'" + func_name + "\'"]
                params.extend(["self.within_history[\'"+ func_name +"\']", str(func_list[-1][2]), str(time_index)])

                output = "self.within(" + ','.join(params) + ")"

        return output



    # Evaluate an operator over a list of boolean results
    def eval_operators(self, current_eval_results, current_operator, \
        event_names, change_of_state, time_index):

        set_eval_result = False
        if "or" in current_operator:
            set_eval_result = any(current_eval_results)
        elif "and" in current_operator:
            set_eval_result = all(current_eval_results)
        else:  # no operator means same as AND since we only have one result here.
            set_eval_result = all(current_eval_results)
        
        # Now, if we have a not, flip the result
        if "not" in current_operator:
            set_eval_result = not set_eval_result

        # If the operator is a list, then it takes on several parameters
        if type(current_operator) == list:
            if current_operator[0] == "set_timed" or current_operator[0] == "sequence_timed":
                operator_params = ','.join([str(x) for x in current_operator[1:]])
                eval_str = "self." + current_operator[0]+"("+"event_names,current_eval_results," \
                    + operator_params + ", time_index)"
                set_eval_result = eval(eval_str)

            elif current_operator[0] == "set_untimed" or current_operator[0] == "sequence_untimed":
                eval_str = "self." + current_operator[0]+"("+"event_names,current_eval_results,time_index)"
                set_eval_result = eval(eval_str)

            elif current_operator[0] == "holds":
                operator_params = ','.join([str(x) for x in current_operator[1:]])
                eval_str = "self." + current_operator[0]+"("+"event_names,current_eval_results," \
                    + operator_params + ", time_index)"
                set_eval_result = eval(eval_str)
        
        return set_eval_result


    # Identify what watchboxes are being used, 
    def identify_event_data(self, function_code):

        event_data = []

        # Get the watchbox names
        wb_names = function_code.split("watchboxes[\"")[1:]
        watchbox_names = []
        watchbox_at = []
        for x in wb_names:
            wb_name = x.split("\"].")[0]
            wb_at = int(x.split("at=")[1].split(",")[0])
            watchbox_names.append(wb_name)
            watchbox_at.append(wb_at)
        
        # So get the watchbox and the result at that particular time
        for w_i, wb_name in enumerate(watchbox_names):

            # Get the results for a time
            wb_result = self.watchboxes[wb_name].composition(watchbox_at[w_i], None)
            wb_result = wb_result.get_as_dict()

            event_data.append((wb_name, wb_result))

        return event_data


    # Recursively go through each function, check its previous eval result,
    #  and compute the result
    def recurse_eval(self, function_to_execute, extra_event_data, time_index):

        # If there is only a single item in this function, then just grab the tuple
        if len(function_to_execute) == 1:
            function_to_execute = function_to_execute[0]

        # If the current item is a single statement, then just evaluate it (watchbox statement)
        if type(function_to_execute) == tuple:
            func_name = function_to_execute[0]
            eval_result = eval(function_to_execute[1])
            change_of_state = False

            # Identify the event data
            event_data = self.identify_event_data(function_to_execute[1])
            extra_event_data.append({func_name : event_data})

            # Check if a state has changed
            if self.previous_eval_result[func_name][0] != eval_result:
                self.previous_eval_result[func_name][0] = eval_result
                self.previous_eval_result[func_name][1] += 1
                change_of_state = True


            return eval_result, change_of_state
        else:
            
            results = []
            event_names = []
            eval_change_of_state = False
            eval_operator = function_to_execute[-1]
            for function_tups in function_to_execute[:-1]:
                eval_result, change_of_state = self.recurse_eval(function_tups, extra_event_data, time_index)
                results.append(eval_result)
                if change_of_state:
                    eval_change_of_state = True
                event_names.append(function_tups[0])
            
            # Evaluate all results based on operator
            final_eval_result = self.eval_operators(results, eval_operator, \
                event_names, eval_change_of_state, time_index)

            # If the final_eval_result is positive, get the data from these results

            return final_eval_result, eval_change_of_state

    # For the current time, set the watchbox states
    #  latest_first determines if we are inserting the object in the middle
    #    or appending it later
    def set_watchbox_states_for_time_and_event(self, known_vicinal_events, current_time, latest_first):
        
        wb_state_changed = False

        # Iterate through all watchboxes and their viciinal events, and set up their state
        for wb_key in known_vicinal_events.keys():

            for vicinal_event in known_vicinal_events[wb_key]:

                # Check if the time matches
                if vicinal_event[0] == current_time:
                    
                    curr_objects = {}
                    for x,y in vicinal_event[3].items():
                        curr_obj_item = {"track_id": x, "class": y["prediction"]}
                        curr_objects[x] = curr_obj_item
                    # Set the watchbox state for this watchbox

                    obj_locations = {x:y["bbox_data"] for x,y in vicinal_event[3].items()}
                    new_wb_result = watchboxResult()
                    new_wb_result.directly_set_states(current_time, curr_objects, obj_locations)
                    if latest_first:
                        self.watchboxes[vicinal_event[2]].data.append(new_wb_result)
                    else:
                        self.watchboxes[vicinal_event[2]].data.insert(1, new_wb_result)
                    wb_state_changed = True

        return wb_state_changed

    # Clear watchbox states and make sure they are empty
    def re_initialize_wb_states(self):

        # For all watchboxes, clear and reinitialize.
        for wb_key in self.watchboxes.keys():

            self.watchboxes[wb_key].data = [watchboxResult()]

    # Get the required composition
    def get_required_wb_states(self, functions, wb_histories):

        required_wb_states = []
        # Iterate through functions
        for f_i, func in enumerate(functions):
            
            # Skip operators
            if type(func) != tuple:
                continue

            # Get the text
            func_text = func[1]

            # Iterate through watchbox
            wb_query = wb_histories[f_i]
            wb_names = wb_query[0]
            wb_time_indexes = wb_query[1]

            for wb_i in range(len(wb_names)):
                # Get the composition specified by the query
                required_comp = parse_ae(func_text, wb_i)
                # Get the specific time when this was detected
                current_time_index = -1 - wb_time_indexes[wb_i]
                current_wb_name = wb_names[wb_i]
                object_locations = \
                    self.watchboxes[current_wb_name].data[current_time_index].locations
                object_preds = \
                    self.watchboxes[current_wb_name].data[current_time_index].objects
                current_wb_cam = "cam"+str(self.watchboxes[current_wb_name].camera_id)
                wb_time = self.watchboxes[current_wb_name].data[current_time_index].time
                detection_data = (current_wb_name, wb_time, object_locations, object_preds, current_wb_cam)

                required_wb_states.append((required_comp, detection_data))
            
        return required_wb_states

    # Recursively go through each function, check its previous eval result,
    #  and compute the result
    def recurse_measure(self, function_to_execute, extra_event_data, time_index):

        # If there is only a single item in this function, then just grab the tuple
        if len(function_to_execute) == 1:
            function_to_execute = function_to_execute[0]

        # If the current item is a single statement, then just evaluate it (watchbox statement)
        if type(function_to_execute) == tuple:
            func_name = function_to_execute[0]
            eval_result = eval(function_to_execute[1])
            change_of_state = False

            # Identify the event data
            event_data = self.identify_event_data(function_to_execute[1])
            extra_event_data.append({func_name : event_data})

            # Check if a state has changed
            if self.previous_eval_result[func_name][0] != eval_result:
                self.previous_eval_result[func_name][0] = eval_result
                self.previous_eval_result[func_name][1] += 1
                change_of_state = True


            return eval_result, change_of_state
        else:
            
            results = []
            event_names = []
            eval_change_of_state = False
            eval_operator = function_to_execute[-1]
            for function_tups in function_to_execute[:-1]:
                eval_result, change_of_state = self.recurse_measure(function_tups, extra_event_data, time_index)
                results.append(eval_result)
                if change_of_state:
                    eval_change_of_state = True
                event_names.append(function_tups[0])
            
            # Evaluate all results based on operator
            final_eval_result = self.eval_operators(results, eval_operator, \
                event_names, eval_change_of_state, time_index)

            # If the final_eval_result is positive, get the data from these results

            return final_eval_result, eval_change_of_state


    # Perform evaluation
    def evaluate(self, time_index):

        eval_results = []
        overall_change_of_state = False
        
        eval_indices_to_track = [self.current_index]
        if self.current_index >= len(self.executable_functions):
            return False, False, None, None

        current_evaluated_function = self.executable_functions[self.current_index]
        

        # It is important to note how we are performing evaluation:
        #  Firstly, we obviously have to evaluate the 'current' state we are at in the FSM
        #  However, we must also evaluate certain previous states, as we wish to return an interval when they are true.
        #  So we evaluate everything up to the current state, and for previous states we evaluate them until they become false from true.
        for i in range(0, len(self.executable_functions)):

            # We actually stop in the case of sequences where previous events haven't occurred
            if i > self.current_index:
                continue
            
            # Otherwise, get the current function to execute
            # Remember, we have multiple functions to execute
            
            current_functions = self.executable_functions[i]
            extra_event_data = []
            final_eval_result, change_of_state = self.recurse_eval(current_functions, \
                extra_event_data, time_index)

            if change_of_state:
                overall_change_of_state = True
            eval_results.append(final_eval_result)
        
        current_result = []
        for eval_index in eval_indices_to_track:
            if eval_index < len(eval_results):
                current_result.append(eval_results[eval_index])
                # If the most recent event has occurred, move up our window
                if self.current_index < len(eval_results) and eval_results[self.current_index]:
                    self.current_index += 1

        return eval_results, overall_change_of_state, current_evaluated_function, extra_event_data

    # Check the watchbox history length, and make sure we keep update when necessary
    def update_wb_history(self, current_functions):

        wb_histories = []
        # For each function, identify its name and max history
        for func in current_functions:
            # Skip operators
            if type(func) != tuple:
                continue

            func = func[1] # Get the program component, not the name

            # Get every watchbox name and at operator
            if ".watchboxes[\"" not in func:
                print("ERROR - update history")
            wb_names = func.split(".watchboxes[\"")
            wb_names = [x.split("\"]")[0] for x in wb_names[1:]]

            if "(at=" not in func:
                print("ERROR - update history")
            wb_history_len = func.split("(at=")
            wb_history_len = [x.split(",")[0] for x in wb_history_len[1:]]
            wb_history_len = [int(x) for x in wb_history_len]

            wb_histories.append((wb_names, wb_history_len))

            # Create a dict for the max history per wb
            wb_history_dict = {}
            for wb_i in range(len(wb_names)):
                if wb_names[wb_i] in wb_history_dict.keys():
                    wb_history_dict[wb_names[wb_i]] = max(wb_history_dict[wb_names[wb_i]], wb_history_len[wb_i])
                else:
                    wb_history_dict[wb_names[wb_i]] = wb_history_len[wb_i]

            # Now, update the max history for watchboxes
            for wb_name in wb_history_dict.keys():
                # Pop out items if there are too many
                num_pops = len(self.watchboxes[wb_name].data) - (wb_history_dict[wb_name]+1) - 1
                for i in range(num_pops):
                    self.watchboxes[wb_name].data.pop(-1)
            

        # Return the watchboxes relevant for these functions
        return wb_histories


    # Determine ae satisfaction
    # We iterate backwards in time
    #   - Updating the watchboxes every time
    #   - Checking if any element of the AE is satisfied given the watchbox states
    def check_ae_satisfied(self, current_functions, known_vicinal_events, latest_time):

        ae_satisfied = False
        earliest_start_time = -1

        wb_states_to_check = None

        # Iterate backwards in time
        #  This is used to determine if an AE has occurred
        for i in range(latest_time, -1, -1):

            # First, check if any watchbox state actually changed
            wb_state_changed = \
                self.set_watchbox_states_for_time_and_event(known_vicinal_events, i, False)

            # Now recursively evaluate if a change occurred.
            if wb_state_changed:
                extra_event_data = []
                final_eval_result, change = \
                    self.recurse_measure(current_functions, extra_event_data, latest_time)

                # Given the current function, determine how to clear the watchbox states
                wb_histories = self.update_wb_history(current_functions)
                
                

                if final_eval_result:
                    ae_satisfied = True
                    earliest_start_time = i
                    # Get the required wb states and times
                    wb_states_to_check = self.get_required_wb_states(current_functions, wb_histories)
                    break


        # Clean up wb states
        self.re_initialize_wb_states()

        detection_time = -1
        if ae_satisfied:
            # Now measure precisely when this ae is detected to have occurred
            #  We do this by executing in the correct time order
            for i in range(earliest_start_time, latest_time):
                 # First, check if any watchbox state actually changed
                wb_state_changed = \
                    self.set_watchbox_states_for_time_and_event(known_vicinal_events, i, True)
            
                # Now recursively evaluate if a change occurred.
                if wb_state_changed:
                    extra_event_data = []

                    final_eval_result, change = \
                        self.recurse_measure(current_functions, extra_event_data, latest_time)

                    if final_eval_result:
                        detection_time = i
                        break
        
        # Clean up wb states
        self.re_initialize_wb_states()
        
        return ae_satisfied, detection_time, wb_states_to_check


# Determine the closest AEs given the known vicinal events
    def find_closest_aes(self, known_vicinal_events, latest_time):

        ae_statuses = []

        # Begin our recursive eval from the end
        for i in range(len(self.executable_functions)-1, -1, -1):
            
            # Check if the current executable function has occurred
            current_functions = self.executable_functions[i]
            
            # Get the AE name
            ae_name = [x[0] for x in current_functions]
            if len(current_functions) > 1:
                ae_name[-1] = current_functions[-1]

            # Begin iterating backwards in time
            ae_satisfied, satisfaction_time, wb_states_to_check =\
                self.check_ae_satisfied(current_functions, known_vicinal_events, latest_time)



            # If AE is satisfied, we move on.  
            #  Otherwise, we set this AE as 'not satisfied', and keep moving
            #  Once we have passed through all AEs, we begin a debug process:
            #    - missed AEs are marked, with an upper bound of either
            #       the next ae/end, and lower bound of the previous AE/0.
            #    - in the first pass, we validate all vicinal events for missed AEs
            #    - in the second pass, we have to do something smarter

            ae_statuses.append((ae_name, ae_satisfied, satisfaction_time, wb_states_to_check))

        return ae_statuses   
        
          
          
    # Add the visualization
    def visualize(self, eval_results):

        # First, we have to create an empty image where height is proportionate to 
        #  the number of states
        num_blocks = len(eval_results)
        blank_image = np.zeros((num_blocks*100,500,3), np.uint8)
        blank_image.fill(255) # or img[:] = 255
        
        # Initialize a set of boxes 
        rpos = [[0,0], [500,100]]
        gtext_pos = [250, 20]
        for general_event in eval_results:
            
            # General event name and result
            general_event_name = general_event[2]
            general_event_result = general_event[3]
            # Sub events and their results
            sub_events = general_event[0]
            sub_event_results = general_event[1]
            
            cv2.rectangle(blank_image, rpos[0], rpos[1], color=(0,255,0), thickness=3)
            rpos[0][1] += 100
            rpos[1][1] += 100
            
            cv2.putText(blank_image, general_event_name, gtext_pos, cv2.FONT_HERSHEY_SIMPLEX,\
                        1, (255, 0, 0), 2, cv2.LINE_AA)
            gtext_pos[1] += 100
            
        
            # Now, draw the inner rectangles
            divided_amount = rpos[1][0] // len(sub_events)
            sub_rect_position = [[0,rpos[0][1]+20],[divided_amount,rpos[1][1]]]
            for sub_event_i in range(len(sub_events)):
                
                sub_event_name = sub_events[sub_event_i]
                sub_event_result = sub_event_results[sub_event_i]
                # Place boxes and text
                cv2.rectangle(blank_image, sub_rect_position[0]\
                                , sub_rect_position[1], color=(255,255,0), thickness=2)
                sub_text_pos = sub_rect_position[0]
                sub_text_pos[0] -= 20
                sub_text_pos[0] += divided_amount//2
                cv2.putText(blank_image, general_event_name, sub_text_pos, cv2.FONT_HERSHEY_SIMPLEX,\
                        1, (255, 0, 0), 2, cv2.LINE_AA)
                
                # Update new positions
                sub_rect_position[0][0] += divided_amount
                sub_rect_position[1][0] += divided_amount
                
        
        cv2.imshow("frame", blank_image)