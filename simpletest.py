import urllib, urllib2
import json
import time

def test_local():
    params = urllib.urlencode({"code":json.dumps(open("turner.py").read()), "team":json.dumps("team1")})
    id = int(urllib2.urlopen("http://127.0.0.1:8881/send",params).read())
    print id
    time.sleep(10)
    print "Status result:",json.loads(urllib2.urlopen("http://127.0.0.1:8881/check_status?id=%s" % id).read())

def test_server():
    params = urllib.urlencode({"code":json.dumps(open("turner.py").read()), "team":json.dumps("team1")})
    id = int(urllib2.urlopen("http://ocean-db.no-ip.biz:8989/send",params).read())
    print id
    time.sleep(10)
    print "Status result:",json.loads(urllib2.urlopen("http://ocean-db.no-ip.biz:8989/check_status?id=%s" % id).read())

if __name__ == '__main__':
    test_server()

