from func import core
import discord

class CharSheet:
    def __init__(self):
        self.char_name = ''
        self.char_id = ''
        self.player_name = ''
        self.player_id = ''

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

        self.trauma = []
        self.harm = {}
        self.rerolls = {}

    def parse(self, data):
        self.char_name = data[0]

        self.char_id = data[1].split('Player: ')[0]
        self.char_id = self.char_id.replace('ID: ', '')
        self.char_id = self.char_id.strip()

        # self.player_id = data[1].split('Player: ')[1]
        # self.player_id = self.player_id.strip()
        # self.player_id = core.strip_id(self.player_id)

        # self.player_name =
        # print(f'Player ID: {self.player_id}')
        # print(f'Player Name: {self.player_name}')
        # print(f'Character ID: {self.char_id}')

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

        for i in data:
            if 'Trauma [' in i:
                self.trauma = core.bracket_split(i)

        for i in data:
            if 'Harm [' in i:
                e = core.bracket_split(i)
                self.harm = core.harm_count(e)

        for i in data:
            if 'Rerolls [' in i:
                e = core.bracket_split(i)
                self.rerolls = core.harm_count(e)






    def print(self) -> str:
        # name and character id
        output = ''
        output += f'{self.char_name}\n'
        output += f'ID: {self.char_id}  Player: {self.player_name}\n'

        dash = '\u2014'
        dot = '\u2022'
        space = ' '

        # resistance pips
        output += f'I {dash+space if self.i_pips == 0 else (dot+space)*self.i_pips}'
        output += f'P {dash+space if self.p_pips == 0 else (dot+space)*self.p_pips}'
        output += f'R {dash+space if self.r_pips == 0 else (dot+space)*self.r_pips}\n'

        # skills
        for k, v in self.skills.items():
            if v > 0:
                output += f'{k} {(dot+space)*v}\n'

        # stress
        output += f'Stress {(dot+space)*self.stress}\n'

        # trauma
        output += 'Trauma '
        if len(self.trauma) == 0:
            output += f'[ {dash} ]'
        else:
            for i in self.trauma:
                output += f'[ {i} ]'
        output += '\n'

        # harm
        output += 'Harm '
        if len(self.harm) == 0:
            output += f'[ {dash} ]'
        else:
            sorted_items = sorted(self.harm.items(), key=lambda x: x[1])
            for k, v in sorted_items:
                output += f'[ {k} {(dot+space)*v}] '
        output += '\n'

        # rerolls
        output += 'Rerolls '
        if len(self.rerolls) == 0:
            output += f'[ {dash} ]'
        else:
            sorted_items = sorted(self.rerolls.items(), key=lambda x: x[1])
            for k, v in sorted_items:
                output += f'[ {k} {(dot+space)*v}] '
        output += '\n'
        return output
