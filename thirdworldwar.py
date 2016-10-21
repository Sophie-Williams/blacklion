# coding: utf-8
import requests
import re
from datetime import datetime
import time
from lxml import html

class ThirdWorldWar:

    def __init__(self, username, password, server):
        self.account = {
            'email': username,
            'pass': password,
            'serveur': int(server),
            'connexion': ''
        }
        self.s = requests.session()

    def rLogin(self):
        r = self.s.post('http://www.3gm.fr/index.php', data=self.account)
        r = self.s.get('http://www.3gm.fr/game/index.php')
        return self.isLogged()

    def rTuto(self):
        r = self.s.get('http://www.3gm.fr/game/production.php?tuto=8')

    def rLogout(self):
        r = self.s.get('http://www.3gm.fr/index.php?action=deco')
        return True if not self.isLogged() else False

    def rThis(self, url):
        r = self.s.get(url)
        return r

    def rSendMessageToServer(self, message, token=False):
        r = self.s.get('http://www.3gm.fr/game/tchat.php')
        if token == False:
            b, token = self.getToken(r.content)
            if not b:
                return False
        r = self.s.post('http://www.3gm.fr/game/tchat.php', data={
            'pseudo': self.account['email'],
            'tk': token,
            'message': message,
        })
        return True

    def rSendMessageToAlliance(self, message):
        r = self.s.get('http://www.3gm.fr/game/my_ally.php')
        b, token = self.getToken(r.content)
        print(token)
        if not b:
            return False
        r = self.s.post('http://www.3gm.fr/game/my_ally.php', data={
            'pseudo': self.account['email'],
            'tk': token,
            'message': message,
        })
        return True

    def rSendMessageToUser(self, message, user):
        r = self.s.post('http://www.3gm.fr/game/modules/ajax/ajax_messagerie.php', data={
            'correspondant_post_new': user,
            'message_post_new': message,
            'id_destinataire': "",
        })
        # print(r.content)
        return True

    def rStartBuilding(self, name):
        buildings = self.getBuildings()
        if len(buildings) == 0:
            return False
        for building in buildings:
            if building['name'] != name: continue
            if not building['available']:
                return False
            r = self.s.get('http://www.3gm.fr/game/'+building['page'])
            r, token = self.getToken(r.content)
            if not r:
                return False
            r = self.s.get('http://www.3gm.fr/game/'+building['page']+'?b='+building['name']+'&tk='+token)
            return True

    def rStopBuilding(self, name):
        buildings = self.getBuildings()
        if len(buildings) == 0:
            return False
        for building in buildings:
            if building['name'] != name: continue
            if not building['feed']:
                return False
            r = self.s.get('http://www.3gm.fr/game/'+building['page'])
            r, token = self.getToken(r.content)
            if not r:
                return False
            r = self.s.get('http://www.3gm.fr/game/'+building['page']+'?ub='+building['name']+'&tk='+token)
            return True

    def rTechActivate(self, name):
        r = self.s.get('http://www.3gm.fr/game/techno.php')
        r, token = self.getToken(r.content)
        if not r:
            return False
        r = self.s.get('http://www.3gm.fr/game/techno.php?a=activer&tech=t_'+name.lower()+'&tk='+token)
        return True

    def rTechStart(self, name):
        r = self.s.get('http://www.3gm.fr/game/techno.php')
        r, token = self.getToken(r.content)
        if not r:
            return False
        r = self.s.get('http://www.3gm.fr/game/techno.php?a=lancer&tech=t_'+name.lower()+'&tk='+token)
        return True

    def rMission(self, x, y):
        r = self.s.get('http://www.3gm.fr/game/mission.php')
        r, token = self.getToken(r.content)
        if not r:
            return False
        r = self.s.post('http://www.3gm.fr/game/mission.php', data={
            'tk': token,
            'q_Transporteurs_maritimes': 30,
            'q_Freemens': 0,
            'q_Tanks_urbains': 0,
            'q_Wingfires': 0,
            'q_Croiseurs': 0,
            'x': x,
            'y': y,
            'mission': 'transport',
            'send': ''
        })
        r, token = self.getToken(r.content)
        if not r:
            return False
        r = self.s.post('http://www.3gm.fr/game/mission.php', data={
            'tk': token,
            'q_alliage': 500000,
            'q_silicium': 500000,
            'q_petrole': 500000,
            'q_essence': 500000,
            'q_pieces': 0,
            'q_monnaie': 500000,
            'x': x,
            'y': y,
            'mission': 'transport',
            'q_Transporteurs_maritimes': 30,
            'q_Freemens': 0,
            'q_Wingfires': 0,
            'q_Croiseurs': 0,
            'send2': '',
            'speed': 500
        })
        return True

    def getMap(self, x, y):
        r = self.s.get('http://www.3gm.fr/game/map.php?x='+str(x)+'&y='+str(y))
        t = html.fromstring(r.content)
        bases = t.xpath('//div[@class="infos_map"]/div/text()')
        coords = t.xpath('//div[@class="img_action"]/a/@href')
        f_bases = []
        n = 0
        i = 0
        for b in bases:
            if b.strip() != "":
                if i == 0:
                    f_bases.insert(n, {
                        'name': b.strip()
                    })
                    i = i+1
                elif i == 1:
                    f_bases[n]['user'] = b.strip()
                    i = 0
                    n = n+1
        n = 0
        i = False
        for c in coords:
            if 'msg.php' in c:
                if i == True:
                    n = n +1
                elif i == False:
                    i = True
            elif 'mission.php' in c:
                m = re.search("x=([0-9]+)&y=([0-9]+)", c)
                if m != None:
                    f_bases[n]['x'] = m.group(1)
                    f_bases[n]['y'] = m.group(2)
        return f_bases

    def getChatAlliance(self):
        r = self.s.get('http://www.3gm.fr/game/my_ally.php')
        # remove all br tags because xpath consider a text with it like a new div (message)
        code = r.content
        code = re.sub('<br />','', code)
        # after continue simply
        t = html.fromstring(code)
        text = t.xpath('//div[@class="centre_content_texte"]/div/div/div/text()')
        stamps = t.xpath('//div[@class="centre_content_texte"]/div/div/div/div/text()')
        messages = []
        for t in text:
            if t.strip() != "":
                messages.insert(len(messages), t.strip())
        chat = []
        for m, s in zip(messages, stamps):
            # need to remove the a with accent
            timestamp = s.split(' ')
            if len(timestamp) == 3:
                timestamp = timestamp[0]+' '+timestamp[2]
            else :
                now = datetime.now()
                timestamp = str(now.day)+'-'+str(now.month)+'-'+str(now.year)+' '+timestamp[0]
            # ready for conversion to datetime object and to timestamp
            timestamp = datetime.strptime(timestamp, '%d-%m-%Y %Hh%M')
            timestamp = int(time.mktime(timestamp.timetuple()))
            chat.insert(len(chat), {
                'date': s,
                'message': m,
                'timestamp': timestamp,
                'elasped': int(time.time())-timestamp
            })
        return chat

    def getBuildings(self):
        buildings = []
        pages = ['build.php', 'production.php', 'army.php']
        for page in pages:
            r = self.s.get('http://www.3gm.fr/game/'+page)
            t = html.fromstring(r.content)
            buildName = t.xpath('//div[@class="build_top_titre"]/text()')
            buildLevl = t.xpath('//div[@class="build_top_niveau"]/span/text()')
            buildAble = t.xpath('//div[@class="build_content"]/div/a/@href')
            for name, lvl in zip(buildName, buildLevl):
                can_build = False
                in_feed = False
                if any(name in links for links in buildAble):
                    can_build = True
                    for link in buildAble:
                        if name in link:
                            m = re.search("ub=", link)
                            if m != None:
                                can_build = False
                                in_feed = True
                buildings.insert(-1, {
                    'name': name,
                    'level': lvl,
                    'available': can_build,
                    'feed': in_feed,
                    'page': page
                })
        return buildings

    def getTechnology(self):
        r = self.s.get('http://www.3gm.fr/game/techno.php')
        t = html.fromstring(r.content)
        techs = t.xpath("//div[@class='info_hover_general']/span/text()")
        links = t.xpath("//div[contains(@id, 'sous_techno_t_')]/div/div/a/@href")
        costs = t.xpath("//div[@class='points_budget']/div[not(@class)]/text()")
        lvmax = t.xpath("//div[contains(@id, 'sous_techno_t_')]/div[not(@class)]/div[not(@class)]/text()")
        new_lvlmax = []
        i = 0
        for lvl_max in lvmax:
            bkup = lvl_max
            lvl_max = lvl_max.strip()
            if lvl_max != "" and len(lvl_max) <4:
                new_lvlmax.insert(i, int(lvl_max.split('/')[1]))
                i = i+1
        lvmax = new_lvlmax
        technos = []
        for tech, lvl_max in zip(techs, lvmax):
            m = re.search('\(([0-9]+)\)', tech)
            if m != None:
                can_build = False
                in_feed = False
                can_activate = False
                name = tech.split(' ')[0]
                level = int(m.group(1))
                for l in links:
                    if name.lower() in l:
                        m = re.search('a=stop', l)
                        m2 = re.search('a=activer', l)
                        if m != None and m2 == None:
                            in_feed = True
                        elif m == None and m2 != None:
                            can_activate = True
                        else :
                            can_build = True
                        break
                cost = False
                if level != lvl_max:
                    cost = costs.pop(0)
                technos.insert(-1, {
                    'name': name,
                    'available': can_build,
                    'feed': in_feed,
                    'activable': can_activate,
                    'level': level,
                    'level_max': lvl_max,
                    'cost': cost
                })
        return technos


    def getTroops(self):
        r = self.s.get('http://www.3gm.fr/game/troops.php')
        t = html.fromstring(r.content)
        trpName = t.xpath('//div[@class="build_top_titre"]/text()')
        trpNumber = t.xpath('//div[@class="build_top_niveau"]/span/text()')
        troops = []
        for name, qty in zip(trpName, trpNumber):
            qty = re.sub('[.]', '', qty)
            troops.insert(-1, {
                'name': name,
                'qty': int(qty)
            })
        return troops

    def getTroopsAvailable(self):
        r = self.s.get('http://www.3gm.fr/game/mission.php')
        t = html.fromstring(r.content)
        trpName = t.xpath('//div[@class="rapport_th"]/text()')
        trpNumber = t.xpath('//div[@class="rapport_td"]/text()')
        for i in range(0,3): trpName.pop(0)
        troops = []
        for name, qty in zip(trpName, trpNumber):
            qty = re.sub('[.]', '', qty)
            troops.insert(-1, {
                'name': name,
                'qty': int(qty)
            })
        return troops

    def getDefenses(self):
        r = self.s.get('http://www.3gm.fr/game/defense.php')
        t = html.fromstring(r.content)
        defName = t.xpath('//div[@class="build_top_titre"]/text()')
        defNumber = t.xpath('//div[@class="build_top_niveau"]/span/text()')
        defenses = []
        for name, qty in zip(defName, defNumber):
            qty = re.sub('[.]', '', qty)
            defenses.insert(-1, {
                'name': name,
                'qty': int(qty)
            })
        return defenses

    def getFeeds(self):
        r = self.s.get('http://www.3gm.fr/game/index.php')
        t = html.fromstring(r.content)
        feeds = [
            {'name': 'Buildings', 'keywords': 'en construction'},
            {'name': 'Units', 'keywords': 'Unit'},
            {'name': 'Technologies', 'keywords': 'Technologies en recherche'},
            {'name': 'Defenses', 'keywords': 'fenses en cours de cr'},
            {'name': 'Troops', 'keywords': 'Mouvements de troupes'}
        ]
        for feed in feeds:
            qty_value = t.xpath('//div[@class="centre_content_title" and contains(text(),"'+feed['keywords']+'")]/span/text()')
            if len(qty_value) > 0:
                qty = qty_value[0].split('/')
                if len(qty) > 1:
                    qty = [int(qty[0]), int(qty[1])]
                else :
                    qty = [int(qty[0]), 0]
            else : qty = [0,0]
            feed.pop('keywords', None)
            feed['actives'] = qty[0]
            feed['max'] = qty[1]
        return feeds

    def isLogged(self):
        r = self.s.get('http://www.3gm.fr/game/index.php')
        tree = html.fromstring(r.content)
        nav = tree.xpath('//div[@id="gauche"]/div[@class="menu"]/a/@href')
        if len(nav) == 0 or '../index.php?action=deco' not in nav:
            return False
        return True

    def getToken(self, code=False):
        if not code:
            r = self.s.get('http://www.3gm.fr/game/index.php')
            code = r.content
        expr = [
            '&tk=([a-z0-9]+)',
            'tk=([a-z0-9]+)',
            "name='tk' value='([a-z0-9]+)'",
            "<input type=hidden value='([a-z0-9]+)' name='tk' \/>",
            "<input type='hidden' name='tk' value='([a-z0-9]+)'/>",
            "<input type=\"hidden\" name=\"tk\" value='([a-z0-9]+)' \/>",
        ]
        token = None
        for e in expr:
            m = re.search(e, code)
            if m != None:
                token = m.group(1)
                break
        if token == None:
            return False, None
        return True, token
