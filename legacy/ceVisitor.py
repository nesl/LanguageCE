from antlr.languageVisitor import languageVisitor  # This is the visitor





class ceVisitor(languageVisitor):

    def __init__(self):

        # Initialize variables

        # Each key is an id to a particular AE or CE.
        #  Each value is a list of tuples, with values flipping between true and false 
        #  for example, [(0, False), (2, True)] means that at timestamp 2, the AE/CE
        #   became true.  By default, every list starts off as false.
        self.state_dict = {}
        self.node_mapping = {}  # Maps a node to a unique ID
        self.camera_node_mapping = {}  # Maps a camera_id to a node_id
        self.current_unique_id = 0

        # Also, keep track of a dictionary that tracks all atomic events
        self.track_atomic_events = True
        self.atomic_events = []

        # Initial ts and data
        self.current_ts = 0
        self.current_data = 0

        # If the complex event itself was updated
        self.updated_root = False

    def addEvent(self, val):

        self.current_ts = val["time"]
        self.current_data = val["results"][0][1][0]
        self.current_camera = val["camera_id"]
        self.updated_root = False

    def updateEventTime(self, new_ts):
        self.current_ts = new_ts
        self.updated_root = False


    # Decide if we need to update the state dict based on previous results
    #  for a particular node.  Remember, we only update the state dict
    #   if an AE/CE value changes (e.g. from true to false or vice versa)
    def updateStateDict(self, node_id, result):
        
        #  Should be [timestamp, truth value]
        previous_state = self.state_dict[node_id][-1]
        if previous_state[1] != result:
            self.state_dict[node_id].append((self.current_ts, result))

            if node_id == 0:
                self.updated_root = True


    def check_and_map_node(self, ctx):

        # Basically just a list of identifiers that we turn into a unique string
        #  Each node has a unique set of children so this should work.
        # node_content = ''.join([str(x) for x in ctx.children])
        node_content = ctx.getText()
        if node_content not in self.node_mapping:
            self.node_mapping[node_content] = self.current_unique_id
            self.current_unique_id += 1
        # If we haven't added this to our state dict, do so.
        current_node_id = self.node_mapping[node_content]
        if current_node_id not in self.state_dict:
            self.state_dict[current_node_id] = [(0, False)]

        return current_node_id

    # Go into state_dict and find the time_intervals for which the node_id
    #  was either true or false
    #  min_time is the minimum time we can look back
    def get_matching_intervals(self, node_id, query_value, min_time):
        
        end_interval = self.current_ts
        node_data = self.state_dict[node_id]

        matched_intervals = []


        # Iterate back through the state_dict (reversed)
        #  Each entry is (timestamp, query value)
        for data_tuple in node_data[::-1]:

            if data_tuple[0] <= min_time:  # Don't look beyond this timestamp
                
                # If this tuple goes beyond the minimum time and matches
                #  our query value, then cut it short and add it to our matches.
                if data_tuple[1] == query_value:
                    matched_intervals.append((min_time, end_interval))
                break

            elif data_tuple[1] == query_value:
                start_interval = data_tuple[0]
                matched_intervals.append((start_interval, end_interval))
            else:
                # This marks when the truth value is no longer true
                end_interval = data_tuple[0]

            

        return matched_intervals

    # Get the numbers for a string (e.g. operatorOptions)
    def splitValues(self, operatorOptions):

        # First, remove brackets
        operatorOptionsValue = operatorOptions.strip("[]")
        # Then split by comma
        operatorOptionsValue = operatorOptionsValue.split(",")
        
        # For each value, split the numerical and string parts
        numerical_vals = []
        units = []
        for option in operatorOptionsValue:
            numerical_val = [i for i in option if i.isdigit()]
            unit_val = [i for i in option if i.isalpha()]
            numerical_val = int(''.join(numerical_val))

            numerical_vals.append(numerical_val)
            units.append(unit_val)

        return numerical_vals, units


    # Evaluate a CE involving an AND
    def evaluateAndEvent(self, child1_id, child2_id, node_id, operatorOptions):

        # First, check when the last time we got an event for this CE
        last_ce_event = self.state_dict[node_id][-1]
        last_ce_event_val = last_ce_event[1]

        # Split the operator options
        #  For AND operations, it should be 
        #  [minimum_interval, maximum_time_looking_back], [units, units]
        operatorOptionValues = self.splitValues(operatorOptions)
        last_ts_to_check = self.current_ts - operatorOptionValues[0][0]
        

        # Check the last time child1, child2 returned true, and record that interval.
        child1_intervals = \
            self.get_matching_intervals(child1_id, True, last_ts_to_check)
        child2_intervals = \
            self.get_matching_intervals(child2_id, True, last_ts_to_check)

        # Evaluate the AND statement
        # First, we iterate through each set of intervals and get the intersection
        and_evaluation = False
        for interval1 in child1_intervals:
            for interval2 in child2_intervals:
                # Calculate the intersection of every two intervals.
                current_interval = (max(interval1[0], interval2[0]), \
                    min(interval1[1], interval2[1]))
                
                # If this interval is valid, then find the difference
                if current_interval[0] < current_interval[1]:
                    interval_difference = current_interval[1] - current_interval[0]
                    requested_value = operatorOptionValues[0][1]
                    
                    # If the interval is valid, we say it is true.
                    if interval_difference >= requested_value:
                        and_evaluation = True

        # Update the state dict (only updates if value changes)
        self.updateStateDict(node_id, and_evaluation)


    def evaluateComplexEvent(self, child1_id, child2_id, node_id, operator, operatorOptions):

        # Perform evaluation of our CE here - check validity for a period of time.
        
        # First type of operator is AND
        if operator == "and":
            self.evaluateAndEvent(child1_id, child2_id, node_id, operatorOptions)

    

    # Evaluate our spatial events
    def visitOverlapExpr(self, ctx):

        # Check the ID
        node_id = self.check_and_map_node(ctx)
        # entity list
        entity_list = []

        # Get entities for each child
        for x in ctx.children:
            if "@" in x.getText():
                entity_list.append(x.getText())

        # Now, evaluate whether this value is true or not.
        #  TO BE IMPLEMENTED

        # For now, assume that camera_id == node_id for evaluation
        result = self.state_dict[node_id][-1][1] # Result is whatever the previous result is
        if self.current_data == "True" and int(self.current_camera) == node_id:
            result = True
        elif self.current_data == "False" and int(self.current_camera) == node_id:
            result = False

        # Add result to the state dictionary
        self.updateStateDict(node_id, result)
        # print(self.state_dict[node_id])

        if self.track_atomic_events:
            self.atomic_events.append((ctx.getText(), node_id))


    def visitWithinExpr(self, ctx):

        # Check the ID
        node_id = self.check_and_map_node(ctx)

        # entity list
        entity_list = []
        bounds = []

        # Print each child
        for x in ctx.children:
            if "@" in x.getText():
                entity_list.append(x.getText())
            elif "[" in x.getText():
                bounds.append(x.getText())

            
    # Evaluate our temporal events
    # This function will have to be re-written at some point as it assumes AEs 
    #  at each child, not CEs.
    def visitComplexEvent(self, ctx):

        # Get the current node ID
        node_id = self.check_and_map_node(ctx)
        

        # Get the first child, which would be an AE or CE
        self.visit(ctx.children[0])
        child_id1 = self.check_and_map_node(ctx.children[0])
        # Get the last child, which would be an AE or CE
        self.visit(ctx.children[3])
        child_id2 = self.check_and_map_node(ctx.children[3])

        # Now, get the operator and parameters
        operatorText = ctx.children[1].getText()
        operatorOptions = ctx.children[2].getText()

        self.evaluateComplexEvent(child_id1, child_id2, node_id, operatorText, operatorOptions)
