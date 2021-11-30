def print_skipevent_msg(reason, evt_num):
    print(f"Skipping event {evt_num}: {reason}")
        
def print_periodic_evtnum(evt_num, n_tot, print_every=500000):
    """Print event info: 'Event `print_every`/`n_tot`.' """
    if (evt_num % print_every) == 0:
        print(f"Processing event {evt_num}/{n_tot}.")