#  Example of our fsm
#    (p1 in watchbox1 and p2 in watchbox2) until/near (p3 in watchbox3)
#           se1                 se2                            se3

#   Initial state - all atomic events false
#  
#   What functions we need to evaluate?
#       - se1 and se2
#       - (se1 and se2) until se3


#   Transitions:
#       - False -> (se1 and se2 True)
#               takes in se1 and se2 and time
#       - (se1 and se2 True) -> entire CE true
#               takes in se3 and time
#       - (se1 and se2 ) -> False
#               takes in se1 and se2, either being false
#       - entire CE true -> (se1 and se2) OR False
#               takes in se1, se2, se3, checks them being false

# One major problem - FSM doesn't know what and/until/near are
#   So these have to be templated transitions?



# Ultimately, a state machine is organized in time - we can only go
#   from one state to another - the user has to specify those transitions
# This is unlike the language where the user has to specify the logic.
# This means we evaluate all atomic events

# Is there a structured way to arrange an FSM with and/until/near?
#  A until B is an FSM where we go (A -> A until B)
#  A and B is an FSM where we go (A -> A and B) or (B -> A and B)
#  A near B is an fsm where we go (A -> A near B) since if A occurs before B
#                                 (B -> B near A) if B occurs before A


from declarativefsm.fsm import FiniteStateMachine

def name_of_global_obj(xx):
    return [objname for objname, oid in globals().items()
            if id(oid)==id(xx)][0]

    return 

# This is a general parser for messages
class 

#  This is the FSM for an "AND" function
class and_fsm(FiniteStateMachine):
    # Initial state.
    initial_state = 'false'

    # Possible transitions.
    transitions = [
        ('false', 'event1'),
        ('false', 'event2'),
        ('event1', 'true'),
        ('event2', 'true'),
        ('event1', 'false'),
        ('event2', 'false'),
        ('true', 'event1'),
        ('true', 'event2'),
    ]

    # Initialize the FSM.
    def __init__(self, event1, event2, *args, **kwargs):
        super(and_fsm, self).__init__(*args, **kwargs)

        self.event1 = event1
        self.event2 = event2

    # Show the current state
    def get_state(self):
        return self.__state__

    # # Handle incoming events.
    def evaluate(self):

        # This is how we transition into different states
        if self.get_state() == "false" and event1.get_state() == "true":
            print("transitioned")


        # if message == 'turn on':
        #     self.transition(to = 'se1 and se2', event = message)
        #     print("turn on")
        # elif message == 'turn off':
        #     self.transition(to = 'entireCE', event = message)
        #     print("turn off")
        # elif message == 'break':
        #     self.transition(to = 'false', event = message)
        #     print("break")