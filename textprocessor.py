import re


class TextProcessor(object):
    SHOT_RE = re.compile(
        '(MISS)?\s*(.+)\s+(\d+)\'\s*(((3PT|Tip|Alley Oop|Cutting|Dunk|Pullup|Turnaround|Running|Driving|Hook|Jump|3pt|Layup|Floating|Fadeaway|Bank|No) ?)+)\s*[Ss]hot\s*\((\d*) PTS\)?\s*\(((.+) (\d+) AST\))?')  # TODO: Track AST,BLK
    REBOUND_RE = re.compile('(.+?) (Rebound|REBOUND)\s*(\(Off:\s*(\d+) Def:\s*(\d+)\))?')
    DEFENSE_RE = re.compile('(.+?) (BLOCK|STEAL) \((\d+) (STL|BLK)\)')
    TIMEOUT_RE = re.compile('([A-Za-z]+) ?Timeout: (Short|Regular|No Timeout|Official)(.*)')
    TURNOVER_RE = re.compile(
        '([A-Za-z0-9 ]+?)\s*(((Out of Bounds|Poss)? ?(- )?(Punched Ball|5 Second|Out Of Bounds|Basket from Below|Illegal Screen|No|Swinging Elbows|Double Dribble|Illegal Assist|Inbound|Palming|Kicked Ball|Jump Ball|Lane|Backcourt|Offensive Goaltending|Discontinue Dribble|Lost Ball|Foul|Bad Pass|Traveling|Step Out of Bounds|3 Second|Offensive Foul|Player Out of Bounds|Turnover) ?)+( Violation| Turnover)?) \(P(\d*)\.T(\d+)\)')
    TEAM_TURNOVER_RE = re.compile(
        '([A-Za-z]+) ?Turnover ?: ((8 Second Violation|5 Sec Inbound|Backcourt|Shot Clock|Offensive Goaltending|3 Second)( Violation)? \(T#(\d+)\)?)')
    FOUL_RE = re.compile(
        '(.+?) Foul: (Clear Path|Flagrant|Away From Play|Personal Take|Inbound|Loose Ball|Offensive|Offensive Charge|Personal|Shooting|Personal Block|Shooting Block|Defense 3 Second)( Type (\d+))? ( )? ')
    JUMP_RE = re.compile('Jump Ball (.+?) vs. (.+):(.*)?')
    VIOLATION_RE = re.compile('(.+?) Violation:(Defensive Goaltending|Kicked Ball|Lane|Jump Ball|Double Lane)( )?')
    FREE_THROW_RE = re.compile('(MISS)?\s*(.+) Free Throw (Flagrant|Clear Path)? ?(\d) of (\d)\s*(\((\d+) PTS\))?')
    TECHNICAL_FT_RE = re.compile('(.+?) Free Throw Technical (Missed)? ?()?')
    SUB_RE = re.compile('(.+?) Substitution replaced by (.+?)$')
    TEAM_VIOLATION_RE = re.compile('Team Violation : (Delay Of Game) ')
    TECHNICAL_RE = re.compile('(.+?) Technical (- )?([A-Z]+)? ?')
    DOUBLE_TECH_RE = re.compile('Double Technical - (.+?), (.+?) ')
    DOUBLE_FOUL_RE = re.compile('Foul : (Double Personal) - (.+?) , (.+?)  ')
    EJECTION_RE = re.compile('(.+?) Ejection:(First Flagrant Type 2|Second Technical|Other)')

    # pts, tov, fta, pf, blk, reb, blka, ftm, fg3a, pfd, ast, fg3m, fgm, dreb, fga, stl, oreb

    def process_item(self, item):
        text = item.get('text', None)
        if text:
            item['events'] = []
        while text:
            l = len(text)
            m = self.SHOT_RE.match(text)
            if m:
                event = {'player': m.group(2), 'dist': m.group(3), 'fga': 1, 'shot_type': m.group(4), '3pa': 0,
                         'shot_made': 0, 'ast_player': None}
                if '3PT' in m.group(4):
                    event['3pa'] = 1
                if m.group(1) is None:
                    event['shot_made'] = 1
                if m.group(9) is not None:
                    event['ast_player'] = m.group(9)
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.REBOUND_RE.match(text)
            if m:
                if (m.group(3) is not None):
                    event = {'player': m.group(1), 'reb': 1, 'oreb_tot': m.group(4), 'dreb_tot': m.group(5)}
                else:
                    event = {'team': m.group(1), 'team_reb': 1, 'reb': 1}
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.DEFENSE_RE.match(text)
            if m:
                event = {'player': m.group(1)}
                if m.group(2) == 'BLOCK':
                    event['blk'] = 1
                else:
                    event['stl'] = 1
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.TIMEOUT_RE.match(text)
            if m:
                event = {'timeout': 1, 'team': m.group(1)}
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.TURNOVER_RE.match(text)
            if m:
                event = {'player': m.group(1), 'tov': 1, 'note': m.group(2), 'team_to': m.group(9),
                         'player_to': m.group(8)}
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.TEAM_TURNOVER_RE.match(text)
            if m:
                event = {'team_tov': 1, 'team': m.group(1), 'note': m.group(3), 'team_to': m.group(5)}
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.FOUL_RE.match(text)
            # TODO: Are all of these actual personal fouls?
            if m:
                event = {'player': m.group(1), 'pf': 1, 'note': m.group(2)}
                if m.group(4):
                    event['type'] = m.group(4)
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.DOUBLE_FOUL_RE.match(text)
            if m:
                item['events'].append({'player': m.group(2), 'pf': 1, 'note': m.group(1), 'against': m.group(3)})
                item['events'].append({'player': m.group(3), 'pf': 1, 'note': m.group(1), 'against': m.group(2)})
                text = text[m.end():].strip()
            m = self.JUMP_RE.match(text)
            if m:
                event = {'jump': 1, 'player_home': m.group(1), 'player_away': m.group(2)}
                if m.group(3):
                    pass
                    # event
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.VIOLATION_RE.match(text)
            if m:
                event = {'player': m.group(1), 'violation': m.group(2)}
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.FREE_THROW_RE.match(text)
            if m:
                event = {'player': m.group(2), 'number': None, 'fta': 1, 'shot_type': 'Free Throw',
                         'fta_no': m.group(4), 'fta_ovr': m.group(5), '3pa': 0,
                         'shot_made': 0, 'ast_player': None}
                if m.group(1) is None:
                    event['shot_made'] = 1
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.TECHNICAL_FT_RE.match(text)
            if m:
                event = {'player': m.group(1), 'fta': 1, 'ftm': 1, 'special': 'Technical'}
                if m.group(2) is None:
                    event['pts'] = 1
                    event['ftm'] = 1
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.SUB_RE.match(text)
            if m:
                item['events'].append({'player': m.group(1), 'sub': 'out'})
                item['events'].append({'player': m.group(2), 'sub': 'in'})
                text = text[m.end():].strip()
            m = self.TEAM_VIOLATION_RE.match(text)
            if m:
                item['team_abbreviation'] = m.group(1)
                text = text[m.end():].strip()
            m = self.TECHNICAL_RE.match(text)
            if m:
                if m.group(3):
                    item['events'].append({'team': m.group(3), 'technical': m.group(1)})
                else:
                    item['events'].append({'player': m.group(1), 'technical': True})
                text = text[m.end():].strip()
            m = self.DOUBLE_TECH_RE.match(text)
            if m:
                item['events'].append({'player': m.group(1), 'technical': True})
                item['events'].append({'player': m.group(2), 'technical': True})
                text = text[m.end():].strip()
            m = self.EJECTION_RE.match(text)
            if m:
                item['events'].append({'player': m.group(1), 'ejection': True, 'note': m.group(2)})
                text = text[m.end():].strip()

            if len(text) == l:
                raise ValueError('Could not parse text: %s' % text)
            if len(text) == 0:
                text = None

        return item
