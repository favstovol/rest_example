from django.contrib.auth.models import User
from django.http import Http404, JsonResponse

from restapp.serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import time
import json
import string


class HomePage(APIView):
    def get(self, request, format=None):
        b = 'bar'
        a = {}
        a = eval('{"asd":"sadsa"}')
        a = {"count": 2, "items": [{"id": 2, "date": 1376054836, "type": "\u0000", "from_id": 2, "read_state": "\u0001", "body": "sad"}, {"id": 1, "date": 1376054836, "type": "\u0000", "from_id": 1, "read_state": "\u0001", "body": "asdasad"}]}
        a = eval('{"count": 2, "items": [{"id": 2, "date": 1376054836, "type": 0, "from_id": 2, "read_state": 1, "body": "sad"}, {"id": 1, "date": 1376054836, "type": 1, "from_id": 1, "read_state": 1, "body": "asdasad"}]}')
        return JsonResponse(a, safe=False)


def find_and_cut(pattern, text):
    ind = text.find(pattern)
    if ind == -1:
        return ''
    sss = text[ind+len(pattern):len(text)]
    ind = sss.find('&')
    if ind != -1:
        sss = sss[0:ind]
    return sss


def find_and_cut_int(pattern, text, initial_value):
    ind = text.find(pattern)
    if ind == -1:
        return initial_value
    sss = text[ind+len(pattern):len(text)]
    ind = sss.find('&')
    if ind != -1:
        sss = sss[0:ind]
    return int(sss)


class UserGet(APIView):
    def get(self, request, st, format=None):
        usrids = find_and_cut('user_ids=', st)
        from django.db import connection
        cursor = connection.cursor()
        fields = "id,first_name,last_name,"+find_and_cut('fields=', st)
        if fields[len(fields)-1] == ',':
            fields = fields[0:-1]
        cursor.execute("SELECT "+fields+" FROM users WHERE id IN("+usrids+") ORDER BY FIELD(id,"+usrids+")")
        if cursor.rowcount == 0:
            return JsonResponse("113", safe=False)
        row = cursor.fetchall()
        kol = len(cursor.description)
        resp = "{'items': ["
        for z in range(cursor.rowcount):
            resp += "{"
            for i in range(kol):
                if type(row[z][i]) == int:
                    resp += "'"+cursor.description[i][0]+"': "+str(row[z][i])+", "
                else:
                    if str(row[z][i]) == '\u0000':
                        resp += "'" + cursor.description[i][0]+"': 0, "
                    elif str(row[z][i]) == '\u0001':
                        resp += "'" + cursor.description[i][0]+"': 1, "
                    else:
                        resp += "'" + cursor.description[i][0]+"': '"+str(row[z][i])+"', "
            resp = resp[0:-2]+"}, "
        if cursor.rowcount != 0:
            resp = resp[0:-2]
        resp += ']}'
        cursor.close()
        connection.close()
        return JsonResponse(eval(resp), safe=False)


class FriendsGetRequests(APIView):
    def get(self, request, st, format=None):
        usrid = int(find_and_cut('user_id=', st))
        ot = find_and_cut_int('out=', st, 0)
        offset = find_and_cut_int('offset=', st, 0)
        count = min(25, find_and_cut_int('count=', st, 25))
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) from friends WHERE id1="+str(usrid)+" AND status="+str(2-ot))
        row = cursor.fetchone()
        kol = str(row[0])
        cursor.execute("SELECT (id2) FROM friends WHERE id1="+str(usrid)+" AND status="+str(2-ot)+" LIMIT "+str(offset)+","+str(count))
        resp = "{'count': "+kol+", 'items': ["
        if cursor.rowcount == 0:
            resp += '  '
        for i in range(cursor.rowcount):
            row = cursor.fetchone()
            resp += "{'user_id': "+str(row[0])+'}, '
        resp = resp[0:-2]
        resp += ']}'
        cursor.close()
        connection.close()
        return JsonResponse(eval(resp), safe=False)


class FriendsAdd(APIView):
    def get(self, request, st, format=None):
        usrid1 = int(find_and_cut('user_id1=', st))
        usrid2 = int(find_and_cut('user_id2=', st))
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM friends WHERE (id1="+str(usrid1)+') AND (id2='+str(usrid2)+')')
        row = cursor.fetchone()
        if cursor.rowcount == 0:
            resp = "1"
            cursor.execute("INSERT INTO friends (id1, id2, status) VALUES("+str(usrid1)+","+str(usrid2)+",1)")
            cursor.execute("INSERT INTO friends (id1, id2, status) VALUES("+str(usrid2)+","+str(usrid1)+",2)")
        else:
            if (row[2] == 5) or (row[2] == 1) or (row[2] == 3):
                resp = "4"
            else:
                if row[2] == 2:
                    resp = "2"
                    cursor.execute("UPDATE friends SET status=5 WHERE (((id1="+str(usrid1)+') AND (id2='+str(usrid2)+')) OR ((id1='+str(usrid2)+') AND (id2='+str(usrid1)+')))')
                else:
                    cursor.execute("SELECT * FROM friends WHERE (id2="+str(usrid1)+') AND (id1='+str(usrid2)+')')
                    row = cursor.fetchone()
                    if row[2] == 3:
                        resp = "2"
                        cursor.execute("UPDATE friends SET status=5 WHERE (((id1="+str(usrid1)+') AND (id2='+str(usrid2)+')) OR ((id1='+str(usrid2)+') AND (id2='+str(usrid1)+')))')
                    else:
                        resp = "1"
                        cursor.execute("UPDATE friends SET status=3 WHERE ((id1="+str(usrid1)+') AND (id2='+str(usrid2)+"))")
        cursor.close()
        connection.close()
        resp = "{'response': "+resp+"}"
        return JsonResponse(eval(resp), safe=False)


class FriendsDelete(APIView):
    def get(self, request, st, format=None):
        usrid1 = int(find_and_cut('user_id1=', st))
        usrid2 = int(find_and_cut('user_id2=', st))
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM friends WHERE (id1="+str(usrid1)+') AND (id2='+str(usrid2)+')')
        row = cursor.fetchone()
        if (cursor.rowcount == 0) or (row[2] == 4):
            resp = "15"
        else:
            if (row[2] == 5) or (row[2] == 2):
                resp = "1"
                if row[2] == 2:
                    resp = "2"
                cursor.execute("UPDATE friends SET status=4 WHERE ((id1="+str(usrid1)+") AND (id2="+str(usrid2)+"))")
                cursor.execute("UPDATE friends SET status=3 WHERE ((id2="+str(usrid1)+") AND (id1="+str(usrid2)+"))")
            else:
                if row[2] == 3:
                    resp = "2"
                    cursor.execute("UPDATE friends SET status=4 WHERE ((id1="+str(usrid1)+") AND (id2="+str(usrid2)+"))")
                else:
                    resp = "2"
                    cursor.execute("UPDATE friends SET status=4 WHERE (((id1="+str(usrid1)+") AND (id2="+str(usrid2)+")) OR ((id1="+str(usrid2)+') AND (id2='+str(usrid1)+')))')
        cursor.close()
        connection.close()
        resp = "{'response': "+resp+"}"
        return JsonResponse(eval(resp), safe=False)


class FriendsGet(APIView):
    def get(self, request, st, format=None):
        usrid = int(find_and_cut('user_id=', st))
        offset = find_and_cut_int('offset=', st, 0)
        from django.db import connection
        cursor = connection.cursor()
        fields = "id,first_name,last_name,"+find_and_cut('fields=', st)
        if fields[len(fields)-1] == ',':
            fields = fields[0:-1]
        cursor.execute("SELECT COUNT(*) FROM friends WHERE ((id1="+str(usrid)+") AND (status=5))")
        row = cursor.fetchone()
        total_kol = str(row[0])
        count = find_and_cut_int('count=', st, total_kol)
        cursor.execute("SELECT "+fields+" FROM users WHERE id IN (SELECT id2 FROM friends WHERE ((id1="+str(usrid)+") AND (status=5)))"+" LIMIT "+str(offset)+","+str(count))
        row = cursor.fetchall()
        kol = len(cursor.description)
        resp = "{'count': "+str(total_kol)+", 'items': ["
        for z in range(cursor.rowcount):
            resp += "{"
            for i in range(kol):
                if type(row[z][i]) == int:
                    resp += "'"+cursor.description[i][0]+"': "+str(row[z][i])+", "
                else:
                    if str(row[z][i]) == '\u0000':
                        resp += "'" + cursor.description[i][0]+"': 0, "
                    elif str(row[z][i]) == '\u0001':
                        resp += "'" + cursor.description[i][0]+"': 1, "
                    else:
                        resp += "'" + cursor.description[i][0]+"': '"+str(row[z][i])+"', "
            resp = resp[0:-2]+"}, "
        if cursor.rowcount != 0:
            resp = resp[0:-2]
        resp += ']}'
        cursor.close()
        connection.close()
        return JsonResponse(eval(resp), safe=False)


class MessagesGet(APIView):
    def get(self, request, st, format=None):
        usrid = int(find_and_cut('user_id=', st))
        tp = find_and_cut_int('type=', st, 0)
        offset = find_and_cut_int('offset=', st, 0)
        count = min(25, find_and_cut_int('count=', st, 25))
        preview_length = find_and_cut_int('preview_length=', st, 0)
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) from messages WHERE user_id="+str(usrid)+" AND type="+str(tp)+" AND deleted=0")
        row = cursor.fetchone()
        total_kol = row[0]
        cursor.execute("SELECT id,date,type,from_id,read_state,body FROM messages WHERE user_id="+str(usrid)+" AND type="+str(tp)+" AND deleted=0 ORDER BY id DESC LIMIT "+str(offset)+","+str(count))
        row = cursor.fetchall()
        kol = len(cursor.description)
        resp = "{'count': "+str(total_kol)+", 'items': ["
        for z in range(cursor.rowcount):
            resp += "{"
            for i in range(kol):
                if type(row[z][i]) == int:
                    resp += "'"+cursor.description[i][0]+"': "+str(row[z][i])+", "
                else:
                    if (cursor.description[i][0] == 'body') and (preview_length != 0):
                        resp += "'"+cursor.description[i][0]+"': '"+str(row[z][i])[0:preview_length]+"', "
                    else:
                        if str(row[z][i]) == '\u0000':
                            resp += "'" + cursor.description[i][0]+"': 0, "
                        elif str(row[z][i]) == '\u0001':
                            resp += "'" + cursor.description[i][0]+"': 1, "
                        else:
                            resp += "'" + cursor.description[i][0]+"': '"+str(row[z][i])+"', "
            resp = resp[0:-2]+"}, "
        if cursor.rowcount != 0:
            resp = resp[0:-2]
        resp += ']}'
        cursor.close()
        connection.close()
        return JsonResponse(eval(resp), safe=False)


class MessagesGetById(APIView):
    def get(self, request, st, format=None):
        msids = find_and_cut('message_ids=', st)
        preview_length = find_and_cut_int('preview_length=', st, 0)
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT id,date,type,from_id,read_state,body FROM messages WHERE id IN ("+msids+") ORDER BY FIELD(id,"+msids+")")
        row = cursor.fetchall()
        kol = len(cursor.description)
        resp = "{'count': "+str(len(row))+", 'items': ["
        for z in range(cursor.rowcount):
            resp += "{"
            for i in range(kol):
                if type(row[z][i]) == int:
                    resp += "'"+cursor.description[i][0]+"': "+str(row[z][i])+", "
                else:
                    if (cursor.description[i][0] == 'body') and (preview_length != 0):
                        resp += "'"+cursor.description[i][0]+"': '"+str(row[z][i])[0:preview_length]+"', "
                    else:
                        if str(row[z][i]) == '\u0000':
                            resp += "'" + cursor.description[i][0]+"': 0, "
                        elif str(row[z][i]) == '\u0001':
                            resp += "'" + cursor.description[i][0]+"': 1, "
                        else:
                            resp += "'" + cursor.description[i][0]+"': '"+str(row[z][i])+"', "
            resp = resp[0:-2]+"}, "
        if cursor.rowcount != 0:
            resp = resp[0:-2]
        resp += ']}'
        cursor.close()
        connection.close()
        return JsonResponse(eval(resp), safe=False)


class MessagesSend(APIView):
    def get(self, request, st, format=None):
        frmid = int(find_and_cut('from_id=', st))
        usrid = int(find_and_cut('user_id=', st))
        ind = st.find("message=☀☃❄☨⑱")
        msg = st[ind+len("message=☀☃❄☨⑱"):len(st)]
        ind = msg.find("✿✞☂☢➵")
        msg = msg[0:ind]
        from django.db import connection
        cursor = connection.cursor()
        d = datetime.now()
        unixtime = time.mktime(d.timetuple())
        cursor.execute("INSERT INTO messages (user_id, from_id, date, read_state, type, body) VALUES("+str(frmid)+","+str(usrid)+","+str(round(unixtime))+",0,1,'"+msg+"')")
        cursor.execute("SELECT LAST_INSERT_ID()")
        row = cursor.fetchone()
        resp = "{'response': "+str(row[0])+"}"
        cursor.execute("INSERT INTO messages (user_id, from_id, date, read_state, type, body) VALUES("+str(usrid)+","+str(frmid)+","+str(round(unixtime))+",0,0,'"+msg+"')")
        cursor.close()
        connection.close()
        return JsonResponse(eval(resp), safe=False)


class MessagesDelete(APIView):
    def get(self, request, st, format=None):
        msids = find_and_cut('message_ids=', st)
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("UPDATE messages SET deleted=1 WHERE id IN ("+msids+")")
        resp = "{'response': 1}"
        cursor.close()
        connection.close()
        return JsonResponse(eval(resp), safe=False)


class MessagesRestore(APIView):
    def get(self, request, st, format=None):
        msids = find_and_cut('message_ids=', st)
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("UPDATE messages SET deleted=0 WHERE id IN ("+msids+")")
        resp = "{'response': 1}"
        cursor.close()
        connection.close()
        return JsonResponse(eval(resp), safe=False)


class MessagesGetDialogs(APIView):
    def get(self, request, st, format=None):
        usrid = int(find_and_cut('user_id=', st))
        offset = find_and_cut_int('offset=', st, 0)
        count = min(25, find_and_cut_int('count=', st, 25))
        preview_length = find_and_cut_int('preview_length=', st, 0)
        unrd = find_and_cut_int('unread=', st, 0)
        from django.db import connection
        cursor = connection.cursor()
        if unrd == 0:
            cursor.execute("SELECT MAX(id) from messages WHERE user_id="+str(usrid)+" AND deleted=0 GROUP BY from_id")
            total_kol = cursor.rowcount
            cursor.execute("SELECT id,date,type,from_id,read_state,body from messages s1 WHERE id=(SELECT MAX(s2.id) from messages s2 WHERE ("+str(usrid)+"=s2.user_id) AND (s2.from_id=s1.from_id) AND (deleted=0)) GROUP BY from_id ORDER BY id DESC LIMIT "+str(offset)+","+str(count))
        else:
            cursor.execute("SELECT MAX(id) from messages WHERE user_id="+str(usrid)+" AND deleted=0 AND read_state=0 GROUP BY from_id")
            total_kol = cursor.rowcount
            cursor.execute("SELECT id,date,type,from_id,read_state,body from messages s1 WHERE id=(SELECT MAX(s2.id) from messages s2 WHERE (s2.user_id="+str(usrid)+") AND (s2.from_id=s1.from_id) AND (deleted=0) AND (read_state=0)) GROUP BY from_id ORDER BY id DESC LIMIT "+str(offset)+","+str(count))
        row = cursor.fetchall()
        kol = len(cursor.description)
        resp = "{'count': "+str(total_kol)+", 'items': ["
        for z in range(cursor.rowcount):
            resp += "{"
            for i in range(kol):
                if type(row[z][i]) == int:
                    resp += "'" + cursor.description[i][0]+"': "+str(row[z][i])+", "
                else:
                    if (cursor.description[i][0] == 'body') and (preview_length != 0):
                        resp += "'" + cursor.description[i][0]+"': '"+str(row[z][i])[0:preview_length]+"', "
                    else:
                        if str(row[z][i]) == '\u0000':
                            resp += "'" + cursor.description[i][0]+"': 0, "
                        elif str(row[z][i]) == '\u0001':
                            resp += "'" + cursor.description[i][0]+"': 1, "
                        else:
                            resp += "'" + cursor.description[i][0]+"': '"+str(row[z][i])+"', "
            resp = resp[0:-2]+"}, "
        if cursor.rowcount != 0:
            resp = resp[0:-2]
        resp += ']}'
        cursor.close()
        connection.close()
        return JsonResponse(eval(resp), safe=False)


class MessagesMarkAsRead(APIView):
    def get(self, request, st, format=None):
        usrid  = find_and_cut_int('user_id=', st, -1)
        msids  = find_and_cut('message_ids=', st)
        prid   = find_and_cut_int('peer_id=', st, -1)
        stmsid = find_and_cut_int('start_message_id=', st, -1)
        from django.db import connection
        cursor = connection.cursor()
        if msids != '':
            zpr = "UPDATE messages SET read_state=1 WHERE id IN ("+msids+")"
        elif stmsid != -1:
            zpr = "UPDATE messages SET read_state=1 WHERE from_id="+str(prid)+" AND id>="+str(stmsid)
        else:
            zpr = "UPDATE messages SET read_state=1 WHERE from_id="+str(prid)
        cursor.execute(zpr)
        resp = "{'response': 1}"
        cursor.close()
        connection.close()
        return JsonResponse(eval(resp), safe=False)


class MessagesGetHistory(APIView):
    def get(self, request, st, format=None):
        usrid = int(find_and_cut('user_id=', st))
        frmid = int(find_and_cut('from_id=', st))
        offset = find_and_cut_int('offset=', st, 0)
        count = min(200, find_and_cut_int('count=', st, 20))
        stmsid = find_and_cut_int('start_message_id=', st, -2)
        rv = find_and_cut_int('rev=', st, 0)
        if rv == 0:
            srv = " DESC "
        else:
            srv = " "
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) from messages WHERE user_id="+str(usrid)+" AND from_id="+str(frmid)+" AND deleted=0")
        row = cursor.fetchone()
        total_kol = row[0]
        cursor.execute("SELECT COUNT(*) from messages WHERE user_id="+str(usrid)+" AND from_id="+str(frmid)+" AND deleted=0 AND read_state=0 AND type=0")
        row = cursor.fetchone()
        kol_unread = row[0]
        if stmsid != -2:
            srv = " DESC "
            if (stmsid == -1) and (kol_unread != 0):
                cursor.execute("SELECT MAX(id) from messages WHERE user_id="+str(usrid)+"AND from_id="+str(frmid)+" AND deleted=0 AND ((read_state=1)OR(type=1))")
                row = cursor.fetchone()
                stmsid = int(row[0])
            if stmsid > 0:
                cursor.execute("SELECT COUNT(*) from messages WHERE user_id="+str(usrid)+" AND from_id="+str(frmid)+" AND deleted=0 AND id>"+str(stmsid))
                row = cursor.fetchone()
                offset += int(row[0])
        cursor.execute("SELECT id,body,user_id,from_id,date,read_state,type FROM messages WHERE user_id="+str(usrid)+" AND from_id="+str(frmid)+" AND deleted=0 ORDER BY id"+srv+"LIMIT "+str(offset)+","+str(count))
        row = cursor.fetchall()
        kol = len(cursor.description)
        resp = "{'count': "+str(total_kol)+", "
        if kol_unread != 0:
            resp += "'unread': "+str(kol_unread)+", "
        resp += "'items': ["
        for z in range(cursor.rowcount):
            resp += "{"
            for i in range(kol):
                if type(row[z][i]) == int:
                    resp += "'"+cursor.description[i][0]+"': "+str(row[z][i])+", "
                else:
                    if str(row[z][i]) == '\u0000':
                        resp += "'" + cursor.description[i][0]+"': 0, "
                    elif str(row[z][i]) == '\u0001':
                        resp += "'" + cursor.description[i][0]+"': 1, "
                    else:
                        resp += "'" + cursor.description[i][0]+"': '"+str(row[z][i])+"', "
            resp = resp[0:-2]+"}, "
        if cursor.rowcount != 0:
            resp = resp[0:-2]
        resp += ']}'
        cursor.close()
        connection.close()
        return JsonResponse(eval(resp), safe=False)
