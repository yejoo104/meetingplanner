
def modify_slots(meeting_length, slot_dict, dates, start_time, end_time):
    """
    modifies the dictionary of slots such that the slot contains information not just about the 30 minute period but about the entire time period of the meeting
        (ex) if meeting length is 2 hours, contains info from 2:00-4:00, 2:30-4:30, 3:00-5:00, etc.
    @param meeting_length(int): length of the meeting, in minutes
    @param slot_dict (dict): dictionary where keys are slots and values are list of names available in that slot
    @param dates (list): list of dates
    @param start_time (int): starting time
    @param end_time (int): ending time
    
    @returns modified_slot_dict (dict): dictionary where keys are slots (indicated by starting time) -- for the length of the meeting_length -- and values are set of names available in that slot
    """
    modified_slot_dict = {}
    
    # Turn meeting_length into number of slots
    num_slots = meeting_length // 30
    
    # Loop through days & time
    for date in dates:
        for time in range(start_time, end_time):
            for timeslot in [str(time) + "00" + str(time) + "30", str(time) + "30" + str(time + 1) + "00"]:
                slot_id = date + timeslot
                people = set(slot_dict[slot_id])
                
                # Loop through number of slots and delete people who can't make it
                for i in range(num_slots - 1):
                    slot_id = next_slot(slot_id)
                    if slot_id not in slot_dict:
                        people = set()
                        break
                    else:
                        people = people.intersection(set(slot_dict[slot_id]))
                
                modified_slot_dict[date + timeslot[:len(timeslot) // 2]] = people
    
    return modified_slot_dict
                
def next_slot(slot):
    """
    returns the chronologically next slot
    
    @param slot(string): slot id input
    @returns next_slot(string): slot id output
    """
    
    start_slot = slot[8: 8 + (len(slot) - 8) // 2]
    hour = int(start_slot[:-2])
    minute = start_slot[-2:]
    
    if minute == "00":
        new_start_slot = str(hour) + "30"
        new_end_slot = str(hour + 1) + "00"
    if minute == "30":
        new_start_slot = str(hour + 1) + "00"
        new_end_slot = str(hour + 1) + "30"
    
    next_slot = slot[:8] + new_start_slot + new_end_slot
    
    return next_slot

def remove_unavailable_slots(slot_dict):
    """
    removes unavailable slots from the slot dictionary
    
    @param slot_dict (dict): dictionary where keys are slots and values are a set of available individuals
    @returns slot_dict (dict): same dictionary as above, but with keys removed when there are no available individuals
    @returns people (list): list of people who are available at least at some point
    """
    
    people = set()
    
    for key in list(slot_dict):
        if len(slot_dict[key]) == 0:
            del slot_dict[key]
        else:
            people = people.union(slot_dict[key])
    
    return slot_dict, list(people)

def schedule(meeting_length, slot_dict, dates, start_time, end_time):
    """
    creates a schedule based on everyone's availability (used: integer linear programming, set cover problem)
    
    @param meeting_length(int): length of the meeting, in minutes
    @param slot_dict (dict): dictionary where keys are slots and values are list of names available in that slot
    @param dates (list): list of dates
    @param start_time (int): starting time
    @param end_time (int): ending time

    @returns schedule(dict): dictionary where keys are slots and values are list of people allocated to the slot
    """
    
    # Modify slot_dict and remove unavailable slots and create people (list of people) and slots (list of slots)
    slot_dict, people = remove_unavailable_slots(modify_slots(meeting_length, slot_dict, dates, start_time, end_time))
    slots = list(slot_dict.keys())

    # Create a matrix where rows are people and columns are slots
    matrix = [[0 for i in range(len(slots))] for j in range(len(people))]
    for key in slot_dict:
        for person in slot_dict[key]:
            matrix[people.index(person)][slots.index(key)] = 1
    print(people, slots, matrix)
    

slot_dict = {"20200809300330": ["A", "B", "C"], "20200809330400": ["A", "B", "D", "E"], "20200809400430": ["B", "E"], "20200809430500": ["A", "D"]}
schedule(30, slot_dict, ["20200809"], 3, 5)
