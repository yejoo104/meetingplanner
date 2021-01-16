
def modify_slots(meeting_length, slot_dict, dates, start_time, end_time):
    """
    modifies the dictionary of slots such that the slot contains information not just about the 30 minute period but about the entire time period of the meeting
        (ex) if meeting length is 2 hours, contains info from 2:00-4:00, 2:30-4:30, 3:00-5:00, etc.
    @param meeting_length(int): length of the meeting, in minutes
    @param slot_dict (dict): dictionary where keys are slots and values are list of names available in that slot
    @param dates (list): list of dates
    @param start_time (int): starting time
    @param end_time (int): ending time
    
    @returns modified_slot_dict (dict): dictionary where keys are slots (indicated by starting time) -- for the length of the meeting_length -- and values are list of names available in that slot
    """
    return {}
