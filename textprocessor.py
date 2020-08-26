import re
from eventTypes import eventTypes

class TextProcessor(object):
    SHOT_RE = re.compile(
        '(MISS)?\s*([^\']+)\s+((\d+)\')?\s*(((3PT|Tip|Alley Oop|Cutting|Dunk|Pullup|Pull-Up|Turnaround|Finger|Roll|Running|Driving|Hook|Putback|Step|Back|Jump|3pt|Layup|Floating|Fadeaway|Reverse|Bank|No) ?)*)\s*([Ss]hot|Layup|Jumper|Dunk)\s*(\((\d*) PTS\))?\s*(\((.+) (\d+) AST\))?')  # TODO: Track AST,BLK
    REBOUND_RE = re.compile('(.+?) (Rebound|REBOUND)\s*(\(Off:\s*(\d+) Def:\s*(\d+)\))?')
    DEFENSE_RE = re.compile('(.+?) (BLOCK|STEAL) \((\d+) (STL|BLK)\)')
    TIMEOUT_RE = re.compile('([A-Za-z]+) ?Timeout: (Short|Regular|No Timeout|Official)(.*)')
    TURNOVER_RE = re.compile(
        '([A-Za-z0-9 \-]+?)\s*(((Out of Bounds|Poss)? ?(- )?(Punched Ball|5 Second|Out Of Bounds|Basket from Below|Illegal Screen|No|Swinging Elbows|Double Dribble|Illegal Assist|Inbound|Palming|Kicked Ball|Jump Ball|Lane|Backcourt|Offensive Goaltending|Discontinue Dribble|Lost Ball|Foul|Bad Pass|Traveling|Step Out of Bounds|3 Second|Offensive Foul|Player Out of Bounds|Violation|Turnover) ?)+( Violation| Turnover)) \(P(\d*)\.T(\d+)\)')
    TEAM_TURNOVER_RE = re.compile(
        '([A-Za-z]+) ?Turnover ?: ((8 Second Violation|5 Sec Inbound|Backcourt|Shot Clock|Offensive Goaltending|3 Second)( Violation)? \(T#(\d+)\)?)')
    FOUL_RE = re.compile(
        '([A-Za-z0-9 \-]+?) (P|S|L|L\.B|OFF|T|Offensive Charge)\.? ?(FOUL|Foul) \((P|T)(\d+).?(.(\d+)\))?.*')
    JUMP_RE = re.compile('Jump Ball (.+?) vs. (.+):(.*)?')
    VIOLATION_RE = re.compile('(.+?) Violation:(Defensive Goaltending|Kicked Ball|Lane|Jump Ball|Double Lane)( )?')
    FREE_THROW_RE = re.compile('(MISS)?\s*(.+) Free Throw (Flagrant|Clear Path)? ?(\d) of (\d)\s*(\((\d+) PTS\))?')
    TECHNICAL_FT_RE = re.compile('(MISS)?\s([A-Za-z0-9 \-]+)? Free Throw Technical')
    SUB_RE = re.compile('SUB: (.+) FOR (.+)')
    TEAM_VIOLATION_RE = re.compile('Team Violation : (Delay Of Game) ')
    TECHNICAL_RE = re.compile('(.+?) Technical (- )?([A-Z]+)? ?')
    DOUBLE_TECH_RE = re.compile('Double Technical - (.+?), (.+?) ')
    DOUBLE_FOUL_RE = re.compile('Foul : (Double Personal) - (.+?) , (.+?)  ')
    EJECTION_RE = re.compile('(.+?) Ejection:(First Flagrant Type 2|Second Technical|Other)')

    # pts, tov, fta, pf, blk, reb, blka, ftm, fg3a, pfd, ast, fg3m, fgm, dreb, fga, stl, oreb

    def process_item(self, item):
        text = item.get('text', None)
        event = {}
        if text:
            l = len(text)
            m = self.SHOT_RE.match(text)
            if m:
                for i in range(1, 15):
                    pass
                    #print(m.group(i))
                event = {'player': m.group(2), 'dist': m.group(4), 'type': eventTypes.SHOT, 'shot_type': m.group(4), '3pa': 0,
                         'shot_made': 0, 'ast_player': None}
                if '3PT' in m.group(5):
                    event['3pa'] = 1
                if m.group(1) is None:
                    event['shot_made'] = 1
                if m.group(12) is not None:
                    event['ast_player'] = m.group(12)
                    event['ast_no'] = m.group(13)
                return event
            m = self.REBOUND_RE.match(text)
            if m:
                if (m.group(3) is not None):
                    event = {'player': m.group(1), 'type': eventTypes.REBOUND, 'oreb_tot': m.group(4), 'dreb_tot': m.group(5)}
                else:
                    event = {'team': m.group(1), 'type': eventTypes.TEAM_REBOUND, 'reb': 1}
                return event
            m = self.DEFENSE_RE.match(text)
            if m:
                event = {'player': m.group(1)}
                if m.group(2) == 'BLOCK':
                    event['type'] = eventTypes.BLK
                else:
                    event['type'] = eventTypes.STL
                return event
            m = self.TIMEOUT_RE.match(text)
            if m:
                event = {'type': eventTypes.TIMEOUT, 'team': m.group(1)}
                return event
            m = self.TURNOVER_RE.match(text)
            if m:
                event = {'player': m.group(1), 'type': eventTypes.TURNOVER, 'note': m.group(2), 'team_to': m.group(9),
                         'player_to': m.group(8)}
                return event
            m = self.TEAM_TURNOVER_RE.match(text)
            if m:
                event = {'type': eventTypes.TEAM_TURNOVER, 'team': m.group(1), 'note': m.group(3), 'team_to': m.group(5)}
                return event
            m = self.FOUL_RE.match(text)
            # TODO: Are all of these actual personal fouls?
            if m:
                event = {'player': m.group(1), 'type': eventTypes.FOUL, 'foul_type': m.group(2)}
                return event
            m = self.DOUBLE_FOUL_RE.match(text)
            if m:
                item['events'].append({'player': m.group(2), 'pf': 1, 'note': m.group(1), 'against': m.group(3)})
                item['events'].append({'player': m.group(3), 'pf': 1, 'note': m.group(1), 'against': m.group(2)})
                return event
            m = self.JUMP_RE.match(text)
            if m:
                event = {'type': eventTypes.JUMP, 'player_home': m.group(1), 'player_away': m.group(2)}
                if m.group(3):
                    pass
                    # event
                return event
            m = self.VIOLATION_RE.match(text)
            if m:
                event = {'player': m.group(1), 'type': eventTypes.VIOLATION, 'note': m.group(2)}
                return event
            m = self.FREE_THROW_RE.match(text)
            if m:
                event = {'player': m.group(2), 'number': None, 'type': eventTypes.FREE_THROW, 'shot_type': 'Free Throw',
                         'fta_no': m.group(4), 'fta_ovr': m.group(5), '3pa': 0,
                         'shot_made': 0, 'ast_player': None}
                if m.group(1) is None:
                    event['shot_made'] = 1
                return event
            m = self.TECHNICAL_FT_RE.match(text)
            if m:
                event = {'player': m.group(2), 'number': None, 'type': eventTypes.FREE_THROW, 'shot_type': 'Free Throw Technical',
                         'fta_no': 1, 'fta_ovr': 1, '3pa': 0,
                         'shot_made': 0, 'ast_player': None}
                if m.group(1) is None:
                    event['shot_made'] = 1
                return event
            m = self.SUB_RE.match(text)
            if m:
                event = {'player_in': m.group(1), 'type': eventTypes.SUB, 'player_out': m.group(2)}
                return event
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
                print(ValueError('Could not parse text: %s' % text))
            if len(text) == 0:
                text = None

        return {type: None}
