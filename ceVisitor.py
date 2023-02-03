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
        self.current_unique_id = 0


    def addEvent(self, val):

        self.current_ts = val[0]
        self.current_data = val[1]

    # Decide if we need to update the state dict based on previous results
    #  for a particular node.  Remember, we only update the state dict
    #   if an AE/CE value changes (e.g. from true to false or vice versa)
    def updateStateDict(self, node_id, result):
        
        #  Should be [timestamp, truth value]
        previous_state = self.state_dict[node_id][-1]
        if previous_state[1] != result:
            self.state_dict[node_id].append([self.current_ts, result])


    def check_and_map_node(self, ctx):

        # Basically just a list of identifiers that we turn into a unique string
        #  Each node has a unique set of children so this should work.
        node_content = ''.join([str(x) for x in ctx.children])
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
    def get_matching_intervals(self, node_id, query_value):
        
        end_interval = self.current_ts
        last_data_tuple = None
        node_data = self.state_dict[node_id]

        # Iterate back through the state_dict (reversed)
        for data_tuple in node_data[::-1]:
            

            if data_tuple[1] == query_value:
                last_ts = data_tuple[0]

        #######
        # Ok, here's what you should be doing:
        #    You should cache the results of matched intervals for each CE
        #    Thus far, you've cached the spatial events, but you are also
        #    recording the results for CEs - 
        #      So if you have a spatial event and a CE that involves it,
        #      you only need to look back in that spatial event as far as
        #      the last CE occurrence.


        return last_ts


    # Evaluate a CE involving an AND
    def evaluateAndEvent(self, child1_id, child2_id, operatorOptions):

        # Check the last time child1, child2 returned true, and record that interval.
        child1_occurred_ts = self.get_matching_intervals(child1_id, True)



    def evaluateComplexEvent(self, child1_id, child2_id, operator, operatorOptions):

        # Perform evaluation of our CE here - check validity for a period of time.
        
        # First type of operator is AND
        if operator == "and":
            self.evaluateAndEvent(child1_id, child2_id, operatorOptions)

    

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
        result = True

        # Add result to the state dictionary
        self.updateStateDict(node_id, result)


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
        self.evaluateComplexEvent(operatorText, operatorOptions)
