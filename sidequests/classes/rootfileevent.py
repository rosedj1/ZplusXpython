class RootFileEvent:

    def __init__(self):
        self.run = None
        self.lumisect = None
        self.event = None
        self.dataset = None
        self.fullpath = None

    def evt_id(self, as_type="str"):
        """
        Return Run, LumiSect, Event as either:
            str. Has the form, "Run:LumiSect:Event"
                Requires `as_type == "str"`.
            tup of ints. Has the form, (Run, LumiSect, Event)
                Requires `as_type == "tup"`.
        """
        if as_type in "str":
            return f"{self.run}:{self.lumisect}:{self.event}"
        elif as_type in "tup":
            return (self.run, self.lumisect, self.event)
        else:
            return None