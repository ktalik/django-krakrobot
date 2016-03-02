# coding: utf-8

import urllib
import urllib2
import json
import os
import time
import subprocess
import uuid

from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.template import RequestContext

import forms
import utils

from models import Submission, Team, Result

SUBMISSION_DEADLINE = time.struct_time([2016, 5, 10, 0, 0, 0, 0, 0, 0])

STATUS_PROCESSING = {"processing": "processing"}


def get_id():
    return uuid.uuid4()

def submit_code(a_code, a_team):
    """
    Save code submission and return id
    """
    id_number = get_id()
    submission = Submission(
        id=id_number,
        team=a_team,
        code=a_code,
    )
    submission.save()
    return id_number


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
    return Submission.objects.filter(team__exact=team)


def get_results(id_number):
    return Result.objects.filter(id__exact=id_number)


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
            id_number = get_id()
            submission = Submission(
                id=id_number,
                team=team,
                package=request.FILES['file']
            )
            submission.save()
            #return HttpResponseRedirect('/success/url/')

            print dir(submission.package)
            print submission.package.path
            print submission.package.url
            
            error = utils.unzip(submission.package.path)
            if error:
                params['error'] = error
                return render_submit(request, params)

            return my_results(request, message='Your code has been sent!')

    return render_submit(request, params)


def xsubmit(request):
    team = get_team(request.user)
    submission_end = time.localtime() > SUBMISSION_DEADLINE

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            instance = ModelWithFileField(file_field=request.FILES['file'])
            instance.save()
            handle_uploaded_file(request.FILES['file'])
            #return HttpResponseRedirect('/success/url/')
            return my_results(request, message='Your code has been sent!')
    else:
        form = UploadFileForm()
    #return render(request, 'upload.html', {'form': form})
    return render(
        request,
        'submission/submit.html',
        {'submission_end': submission_end, 'team': team, 'form': form}
    )


def handle_uploaded_file(f):
    with open('some/file/name.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def old_submit(request):
    if not request.user.is_authenticated():
        return index(request)

    team = get_team(request.user)

    if request.POST:
        base_dir = os.path.dirname(__file__)
        code = request.POST.get('source_code')
        id_number = submit_code(code, team)
        filename = base_dir + '/../src/' + str(id_number) + '.py'

        with open(filename, 'w') as src:
            src.write(code)

        print id_number, 'filename', filename
        cmd = [
            'python2.7', base_dir + '/../bin/simulator/main.py', '-c', '-r',
            # It is important to concatenate strings here
            # It means passing option parameter in quotes: -r "python2.7 path"
            'python2.7 ' + filename]
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        # Log if something bad happened inside subprocess
        print id_number, 'stderr', stderr

        result = '{}'
        lines = ''
        lines = stdout.splitlines()
        result = lines[-1]
        print id_number, 'result', result

        db_result = Result()
        db_result.id = id_number
        db_result.report = result
        db_result.log = stdout + stderr
        print id_number, 'log', db_result.log
        db_result.save()

        return my_results(request, message='Your code has been sent!')

    submission_end = time.localtime() > SUBMISSION_DEADLINE

    return render(
        request,
        'submission/submit.html',
        {'submission_end': submission_end, 'team': team}
    )


def my_results(request, message=''):
    if not request.user.is_authenticated():
        return index(request)

    params = {'submissions': [], 'message': message, 'team': None}
    team = get_team(request.user)
    params['team'] = team
    submissions = get_submissions(team)

    for submission in submissions:
        in_db = False
        results = get_results(submission.id)
        result_string = '{}'
        if len(results) == 0:
            d = STATUS_PROCESSING
        else:
            in_db = True
            result_string = results[0].report
            d = json.loads(result_string)
            d['log'] = results[0].log.splitlines()

            d['picture'] = []
            for r in d['map']['color_board']:
                row = []
                for c in r:
                    # FIXME: white is [0, 0, 0]
                    if c == [0, 0, 0]:
                        c = [255, 255, 255]
                    col = {'color': c}
                    row.append(col)
                d['picture'].append(row)

            for num, beep in enumerate(d['map']['beeps']):
                d['picture'][beep[0]][beep[1]]['beep'] = str(num)

            for r, row in enumerate(d['map']['board']):
                for c, col in enumerate(row):
                    if col == 1:
                        d['picture'][r][c]['wall'] = True
                    elif col == 3:
                        d['picture'][r][c]['start'] = True

            d['test_name'] = d['map']['file_name'].split('/')[-1]

        params["submissions"].append({
            "id": submission.id,
            "results": [d],
            "date": submission.date
        })

        passed = False
        if not ('processing' in d or 'error' in d or 'timed_out' in d):
            if not in_db:
                result_in_db = Result()
                result_in_db.id = submission.id
                result_in_db.report = str(result_string)
                result_in_db.save()
            passed = True
            print d['results']
            for result in d['results']:
                if result == 'error' \
                        or result.get('error', False):
                    passed = False
                    continue
                if not result.get('goal_achieved', False):
                    passed = False
                    continue
        if passed:
            team.passed = True
            team.save()

    params["submissions"].reverse()

    return render(request, 'submission/my_results.html', params)


def results(request):
    teams = Team.objects.all()
    params = {'teams': []}

    for team in teams:
        passed = team.passed
        if team.name != 'TestTeam':
            params["teams"].append({'name': team.name, 'passed': passed})

    params['submission_ended'] = time.localtime() > SUBMISSION_DEADLINE
    return render(request, 'submission/results.html', params)


def logout_user(request):
    params = {'message': 'You are not logged in.'}
    if request.user and request.user.is_authenticated:
        logout(request)
        params = {'message': 'Logged out.'}
    return index(request, params)


def login_user(request):
    state = "Please log in."
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
                message = "Account is not active. Please contact the site admin."
        else:
            message = "Username and/or password incorrect."

        return render_to_response(
            'submission/login.html',
            {
                'message': message,
            },
            context_instance=RequestContext(request)
        )

    return render_to_response(
        'submission/login.html',
        {
            'state': state,
            'username': username
        },
        context_instance=RequestContext(request)
    )
