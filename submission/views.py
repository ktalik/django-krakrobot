# coding: utf-8

import urllib
import urllib2
import json
import os
import time
import stat
import subprocess
import uuid

from django.shortcuts import render_to_response, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

import forms
import utils

from models import Submission, Team, Result

SUBMISSION_DEADLINE = time.struct_time([2016, 5, 10, 0, 0, 0, 0, 0, 0])

RESULT_JSON_FILE_NAME = 'result.json'

TEST_FILE_NAMES = ['1.map', '2.map']


def get_id():
    return uuid.uuid4()


def fetch_status(id_number):
    return u'{"processing": "processing"}'

    try:
        response = urllib2.urlopen(
            TEST_SERVER + 'check_status?id=%s' % id_number,
            timeout=7
        ).read()

        if str(response) and str(response)[0:22] == '"error_checking_status':
                return '{"processing": "processing"}'

        return json.loads(
            response
        )
    #except urllib2.URLError or socket.timeout or urllib2.HTTPError:
    except Exception:  # unknown problem with simulator API
        return {'timed_out': 'timed_out'}


def get_team(user):
    teams = Team.objects.filter(user__exact=user)
    team = None
    if teams:
        team = teams[0]
    return team


def get_submissions(team):
    return Submission.objects.filter(team__exact=team).order_by('-date')


def get_results(id_number):
    return Result.objects.filter(submission_id__exact=id_number)


def index(request, params={}):
    return render(request, 'submission/index.html', params)


def render_submit(request, params={}):
    team = get_team(request.user)
    submission_end = time.localtime() > SUBMISSION_DEADLINE

    if not 'form' in params:
        params['form'] = forms.UploadSubmissionForm()

    params.update({'submission_end': submission_end, 'team': team})

    return render(request, 'submission/submit.html', params)

    
def submit(request):
    team = get_team(request.user)
    params = dict()

    if request.method == 'POST':
        form = forms.UploadSubmissionForm(request.POST, request.FILES)
        params['form'] = form

        if form.is_valid():
            submission = Submission(
                team=team,
                package=request.FILES['file'],
                user=request.user,
            )
            submission.save()

            error = utils.unzip(submission.package.path)
            if error:
                submission.delete()
                params['error'] = error
                return render_submit(request, params)

            try:
                execute_tester(submission)
            except Exception as error:
                report = 'Blad wewnetrzny testerki: ' + str(error)
                print 'ERROR:', report
                db_result = Result()
                db_result.submission_id = submission.id
                db_result.report = json.dumps({'error': report})
                db_result.log = ''
                db_result.save()

            return my_results(
                request, message=_(u'Rozwiązanie zostało wysłane.'))

    return render_submit(request, params)


def execute_tester(submission):
    s_id = submission.id
    (s_path, s_pkg_name) = os.path.split(submission.package.path)

    # Move to the submission directory
    os.chdir(s_path)

    s_cmd = './run.sh'
    if not os.path.exists(s_cmd):
        s_cmd = './run.py'
        if not os.path.exists(s_cmd):
            db_result = Result()
            db_result.submission_id = s_id
            db_result.report = json.dumps(
                {'error': 'Brakuje `run.sh` lub `run.py`!'})
            db_result.log = ''
            db_result.save()
            return

    submission.command = s_cmd
    submission.save()

    s_cmd = os.path.join(s_path, s_cmd)

    os.chmod(s_cmd, stat.S_IEXEC | stat.S_IREAD)
    
    for test in TEST_FILE_NAMES:
        map_path = os.path.join(
            settings.STATIC_ROOT, 'maps', test)
        result_file_name = os.path.join(
            s_path, test + '_' + RESULT_JSON_FILE_NAME)

        if not os.path.exists(result_file_name):
            open(result_file_name, 'w').close() 

        cmd = [
            'python2.7',
            os.path.join(settings.BIN_DIR, 'simulator/main.py'),
            '-c',
            '--map', map_path,
            '--robot', s_cmd,
            '--output', result_file_name
        ]
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()

        # Log testing process here
        print s_id, 'stderr', stderr

        # Log result
        lines = stdout.splitlines()
        result = json.load(open(result_file_name))

        db_result = Result()
        db_result.submission_id = s_id
        db_result.report = json.dumps(result)
        print s_id, 'report', db_result.report
        db_result.log = stdout + stderr
        db_result.save()
        print '\n\nResult saved.\n\n'


def my_results(request, message=''):
    if not request.user.is_authenticated():
        return index(request)
    
    response_params = {
        'submissions': [],
        'message': message,
        'team': None
    }

    team = get_team(request.user)
    if team:
        response_params['team'] = team

    submissions = get_submissions(team)

    for submission in submissions:
        submission_dict = {
            'status': 'processing',
            'user': submission.user.username
        }

        results = get_results(submission.id)
        results_descriptions = []
        results_dicts = []
        if results:
            results_dicts = describe_results(results)

        submission_dict.update({
            "id": submission.id,
            "results": results_dicts,
            "date": submission.date
        })

        if results:
            submission_dict['status'] = 'finished'

        response_params['submissions'].append(submission_dict)

    return render(request, 'submission/my_results.html', response_params)


def describe_results(results):
    ''' Generate a descriptive dict with results details from a Result model '''
    if not results:
        return []

    results_dicts = []
    for result in results:
        result_string = '{}'
        if len(results) == 0:
            d = STATUS_PROCESSING
        else:
            in_db = True
            result_string = result.report

            if not result_string:
                d = {"error": "No result"}
                results_dicts.append(d)
                break

            d = json.loads(result_string)
            if 'error' in d and d['error']:
                results_dicts.append(d)
                break

            d['log'] = result.log.splitlines()

            d['picture'] = []

            map_json = json.load(open(d.get('map', {}).get('file_name', '')))

            d['svg'] = os.path.join(
                settings.STATIC_URL,
                'maps',
                map_json.get('vector_graphics_file', '')
            )
            
            for r in d.get('map', {}).get('board', []):
                row = []
                for c in r:
                    # FIXME: white is [0, 0, 0]
                    col = {'color': c}
                    row.append(col)
                d['picture'].append(row)

            for num, beep in enumerate(d['beeps']):
                d['picture'][int(beep[0])][int(beep[1])]['beep'] = str(num)

            for r, row in enumerate(d.get('map', {}).get('board', {})):
                for c, col in enumerate(row):
                    if col == 1:
                        d['picture'][r][c]['wall'] = True
                    elif col == 3:
                        d['picture'][r][c]['start'] = True

            d['test_name'] = d.get(
                'map', {}
            ).get('file_name', 'No name').split('/')[-1]

            results_dicts.append(d)

    return results_dicts


def results(request):
    teams = Team.objects.all()
    params = {'teams': []}

    for team in teams:
        passed = team.passed
        if team.name != 'TestTeam':
            params["teams"].append(
                {'name': team.name, 'passed': passed, 'avatar': team.avatar})

    params['submission_ended'] = time.localtime() > SUBMISSION_DEADLINE
    return render(request, 'submission/results.html', params)


def logout_user(request):
    params = {'message': _('Nie jesteś zalogowany(a).')}
    if request.user and request.user.is_authenticated:
        logout(request)
        params = {'message': _(u'Wylogowano.')}
    return index(request, params)


def login_user(request):
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('./..')
            else:
                error = _(u'Konto nie jest aktywne. Zgłoś ten błąd do nas.')
        else:
            error = _(u'Nieprawidłowy login lub hasło!')

        return render_to_response(
            'submission/login.html',
            {
                'error': error,
            },
            context_instance=RequestContext(request)
        )

    return render_to_response(
        'submission/login.html',
        {
            'username': username
        },
        context_instance=RequestContext(request)
    )


def change_password(request):
    if not request.user.is_authenticated():
        return index(request)

    user = request.user

    if request.POST:
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        user = authenticate(username=user.username, password=old_password)

        if user is not None:
            user.set_password(new_password)
            user.save()
            params = {'message': _(u'Pomyślnie zmieniono hasło.')}
            return index(request, params)

        else:
            params = {'error': _(u'Nieprawidłowe stare hasło.')}
            return index(request, params)

    return render_to_response(
        'submission/change_password.html',
        {
            'username': username
        },
        context_instance=RequestContext(request)
    )
