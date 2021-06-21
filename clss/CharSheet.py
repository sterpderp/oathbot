from func import core


class CharSheet:
    def __init__(self):
        self.char_name = ''
        self.char_id = ''

        self.i_pips = 0
        self.p_pips = 0
        self.r_pips = 0

        self.skills = {
            "Hunt": 0,
            "Study": 0,
            "Survey": 0,
            "Tinker": 0,

            "Finesse": 0,
            "Prowl": 0,
            "Skirmish": 0,
            "Wreck": 0,

            "Aether": 0,
            "Command": 0,
            "Consort": 0,
            "Sway": 0
        }

        self.stress = 0

        self.trauma = ['[ — ]']
        self.harm = ['[ — ]']
        self.rerolls = ['[ — ]']

    def parse(self, data):
        self.char_name = data[0]
        self.char_id = data[1]

        _ipr = core.ipr_split(data[2])
        self.i_pips = _ipr[0]
        self.p_pips = _ipr[1]
        self.r_pips = _ipr[2]

        for i in data:
            for j in self.skills:
                if j in i:
                    self.skills[j] = i.count('•')
                else:
                    pass
        for i in data:
            if 'Stress' in i:
                self.stress = i.count('•')
