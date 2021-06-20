class CharSheet:
    def __init__(self):
        self.char_name = ''
        self.char_id = ''

        self.i_pips = 0
        self.p_pips = 0
        self.r_pips = 0

        self.skills = {
            "hunt": 0,
            "study": 0,
            "survey": 0,
            "tinker": 0,

            "finesse": 0,
            "prowl": 0,
            "skirmish": 0,
            "wreck": 0,

            "aether": 0,
            "command": 0,
            "consort": 0,
            "sway": 0
        }

        self.stress = 0

        self.trauma = []
        self.harm = []
        self.rerolls = []
