import random
from abc import ABC
from typing import List
from .GameChar import GameChar
from .interact import UI
import asyncio

class Gaming(ABC):
    def __init__(self, team_a: List[dict], team_b: List[dict], ui: UI):
        self.team_a = [GameChar(x) for x in team_a]
        self.team_b = [GameChar(x) for x in team_b]
        self.turn = 1
        self.ui = ui

    async def start(self):
        while True:
            # 获胜状态判断
            if len(self.team_a) == 0 and len(self.team_b) == 0:
                return 'all_dead'
            if len(self.team_a) == 0:
                return 'b_win'
            if len(self.team_b) == 0:
                return 'a_win'

            self.ui.append('回合数：{}'.format(self.turn))

            # 技能发动、攻击、效果执行
            # 然后buff结算、减冷却
            self._skill_check('a')
            self._status_manage('a')

            self._skill_check('b')
            self._status_manage('b')

            self.team_a = self._death_check('a')
            self.team_b = self._death_check('b')

            self._display_status()
            await self.ui.send()

            self.turn += 1

            # await asyncio.sleep(16)

    def selector(self, target, team_name: str, initiator: GameChar):
        type_ = target['type']
        if type_ == 'SELF':
            return [initiator]
        if type_ == 'OTHER':
            return list(filter(lambda x: x is not initiator, self._get_team(team_name)))

        if target['team'] == 0:
            team_name = {'a': 'b', 'b': 'a'}[team_name]
        team = self._get_team(team_name)

        if type_ == 'ALL':
            return team
        if type_ == 'RAND':
            result = team * (target['limit'] // len(team)) + random.sample(team, target['limit'] % len(team))
            random.shuffle(result)
            return result

        key, reverse = {
            'LIFEMOST': (lambda x: x.hp_percentage, True),
            'LIFELEAST': (lambda x: x.hp_percentage, False),
            'ATKMOST': (lambda x: x.attack, True),
            'ATKLEAST': (lambda x: x.attack, False)
        }[type_]
        return sorted(team, key=key, reverse=reverse)[:target['limit']]

    def _death_check(self, team_name):
        team = self._get_team(team_name)

        now_team = []
        for chara in team:
            if chara.not_dead:
                now_team.append(chara)
            else:
                pass
                # TODO 汇报死亡消息

        return now_team

    def _skill_check(self, team_name):
        team = self._get_team(team_name)

        for chara in team:
            skill_gotten = chara.skill_activate()
            if skill_gotten is not None:
                for skill in skill_gotten:
                    self.ui.append(f'[{chara.name}] 使用了 "{skill["name"]}"')
                    feedback = []
                    for effect in skill['effect']:
                        selected = self.selector(effect['target'], team_name, chara)
                        feedback.extend(chara.use_effect(selected, effect))
                    merged = []
                    for f in feedback:
                        for m in merged:
                            if m['feedback'] == f['feedback'] and m['merge_key'] == f['merge_key']:
                                for k, v in f['param'].items():
                                    m['param'][k] += v
                                break
                        else:
                            merged.append(f)
                    if merged:
                        lines = [x['feedback'].format(**x['merge_key'], **x['param']) for x in merged]
                        for line in lines[:-1]:
                            self.ui.append(' ├ ' + line)
                        self.ui.append(' └ ' + lines[-1])

    def _status_manage(self, team_name):
        team = self._get_team(team_name)

        for chara in team:
            chara.buff_fade()
            chara.skill_cooldown()
            chara.turn_mp_gain()

    def _display_status(self):
        self.ui.append('—' * 12)
        for chara in self.team_a:
            self.ui.append('[{name}]{mp}|{hp}'.format(name=chara.name, mp=chara.mp_display(), hp=chara.life_display()))
        self.ui.append('—' * 7)
        for chara in self.team_b:
            self.ui.append('[{name}]{mp}|{hp}'.format(name=chara.name, mp=chara.mp_display(), hp=chara.life_display()))

    def _get_team(self, team_name):
        return getattr(self, f'team_{team_name}')