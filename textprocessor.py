import re
class TextProcessor(object):
    SHOT_RE = re.compile('(MISS)?\s*(.+)\s+(\d+)\'\s*(((Tip|Alley Oop|Cutting|Dunk|Pullup|Turnaround|Running|Driving|Hook|Jump|3pt|Layup|Floating|Fadeaway|Bank|No) ?)+)\s*[Ss]hot\s*((\d*) PTS)?\s*((.+) (\d+) AST)?') #TODO: Track AST,BLK
    REBOUND_RE = re.compile('(.+?) Rebound ')
    TEAM_REBOUND_RE = re.compile('Team Rebound')
    DEFENSE_RE = re.compile('(Block|Steal): ?(.+?) ')
    ASSIST_RE = re.compile('Assist: (.+?) ')
    TIMEOUT_RE = re.compile('Team Timeout : (Short|Regular|No Timeout|Official)')
    TURNOVER_RE = re.compile('(.+?) Turnover : ((Out of Bounds|Poss)? ?(- )?(Punched Ball|5 Second|Out Of Bounds|Basket from Below|Illegal Screen|No|Swinging Elbows|Double Dribble|Illegal Assist|Inbound|Palming|Kicked Ball|Jump Ball|Lane|Backcourt|Offensive Goaltending|Discontinue Dribble|Lost Ball|Foul|Bad Pass|Traveling|Step Out of Bounds|3 Second|Offensive Foul|Player Out of Bounds)( Violation)?( Turnover)?) ')
    TEAM_TURNOVER_RE = re.compile('Team Turnover : ((8 Second Violation|5 Sec Inbound|Backcourt|Shot Clock|Offensive Goaltending|3 Second)( Violation)?( Turnover)?)')
    FOUL_RE = re.compile('(.+?) Foul: (Clear Path|Flagrant|Away From Play|Personal Take|Inbound|Loose Ball|Offensive|Offensive Charge|Personal|Shooting|Personal Block|Shooting Block|Defense 3 Second)( Type (\d+))? ( )? ')
    JUMP_RE = re.compile('Jump Ball (.+?) vs (.+)( )?')
    VIOLATION_RE = re.compile('(.+?) Violation:(Defensive Goaltending|Kicked Ball|Lane|Jump Ball|Double Lane)( )?')
    FREE_THROW_RE = re.compile('(.+?) Free Throw (Flagrant|Clear Path)? ?(\d) of (\d) (Missed)? ?()?')
    TECHNICAL_FT_RE = re.compile('(.+?) Free Throw Technical (Missed)? ?()?')
    SUB_RE = re.compile('(.+?) Substitution replaced by (.+?)$')
    TEAM_VIOLATION_RE = re.compile('Team Violation : (Delay Of Game) ')
    CLOCK_RE = re.compile('qfafdaf')
    TEAM_RE = re.compile('afdsdqfafd')
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
                print(m.group(1))
                print(m.group(2))
                print(m.group(3))
                print(m.group(4))
                print(m.group(5))
                print(m.group(6))
                print(m.group(7))
                print(m.group(8))
                print(m.group(9))
                print(m.group(10))
                event = {'player': m.group(1), 'fga': 1, 'type': m.group(2)}
                if '3pt' in m.group(2):
                    event['fg3a'] = 1
                    if m.group(5) == 'Made':
                        event['fg3m'] = 1
                        event['fgm'] = 1
                        event['pts'] = 3
                else:
                    if m.group(5) == 'Made':
                        event['fg3m'] = 1
                        event['fgm'] = 1
                        event['pts'] = 2
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.REBOUND_RE.match(text)
            if m:
                event = {'player': m.group(1), 'reb': 1}
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.DEFENSE_RE.match(text)
            if m:
                event = {'player': m.group(2)}
                if m.group(1) == 'Block':
                    item['events'][-1]['blka'] = 1
                    event['blk'] = 1
                else:
                    event['stl'] = 1
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.ASSIST_RE.match(text)
            if m:
                event = {'player': m.group(1), 'ast': 1}
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.TIMEOUT_RE.match(text)
            if m:
                event = {'timeout': m.group(1)}
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.TURNOVER_RE.match(text)
            if m:
                event = {'player': m.group(1), 'tov': 1, 'note': m.group(2)}
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.TEAM_TURNOVER_RE.match(text)
            if m:
                event = {'turnover': m.group(1)}
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.TEAM_REBOUND_RE.match(text)
            if m:
                item['events'].append({'rebound': 'team'})
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
                item['events'].append({'player': m.group(1), 'jump': 'home'})
                item['events'].append({'player': m.group(2), 'jump': 'away'})
                if m.group(3):
                    item['events'].append({'player': m.group(4), 'jump': 'possession'})
                text = text[m.end():].strip()
            m = self.VIOLATION_RE.match(text)
            if m:
                event = {'player': m.group(1), 'violation': m.group(2)}
                item['events'].append(event)
                text = text[m.end():].strip()
            m = self.FREE_THROW_RE.match(text)
            if m:
                event = {'player': m.group(1), 'fta': 1, 'attempt': m.group(3), 'of': m.group(4)}
                if m.group(5) is None:
                    event['pts'] = 1
                    event['ftm'] = 1
                if m.group(2):
                    event['special'] = m.group(2)
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
                item['events'].append({'violation': m.group(1)})
                text = text[m.end():].strip()
            m = self.CLOCK_RE.match(text)
            if m:
                print(m)
                item['clock'] = m.group(1)
                text = text[m.end():].strip()
            m = self.TEAM_RE.match(text)
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