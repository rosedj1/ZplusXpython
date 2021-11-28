def print_skipevent_msg(reason, evt_num, verbose):
    if verbose:
        print(f"Skipping event {evt_num}: {reason}")
        
def print_periodic_evtnum(evt_num, n_tot, print_every):
    """Print event info: 'Event `print_every`/`n_tot`.' """
    if (evt_num % print_every) == 0:
        print(f"Processing event {evt_num}/{n_tot}.")