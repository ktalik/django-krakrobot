# Create your views here.

import urllib
import urllib2
import json
import time

from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.template import RequestContext

from submission.models import Submission, Team, Result

TEST_SERVER = "http://188.226.161.198:8989/"
SUBMISSION_DEADLINE = time.struct_time([2014, 3, 10, 0, 0, 0, 0, 0, 0])


def send_code(code, team_name):  # TODO: Move to utils
    params = urllib.urlencode(
        {
            'code': json.dumps(code),
            'team': json.dumps(team_name)
        }
    )
    id_number = int(
        urllib2.urlopen(
            TEST_SERVER + 'send',
            params,
            7
        ).read()
    )
    return id_number


def submit_code(a_code, a_team):  # TODO: Move to utils
    id_number = send_code(a_code, a_team.name)
    submission = Submission(
        api_id=id_number,
        team=a_team,
        code=a_code
    )
    submission.save()
    return id_number


def fetch_status(id_number):  # TODO: Move to utils
    try:
        response = urllib2.urlopen(
            TEST_SERVER + 'check_status?id=%s' % id_number,
            timeout=7
        ).read()

        if str(response) and str(response)[0:22] == '"error_checking_status':
                return {'processing': 'processing'}

        return json.loads(
            response
        )
    #except urllib2.URLError or socket.timeout or urllib2.HTTPError:
    except Exception:  # unknown problem with simulator API
        return {'timed_out': 'timed_out'}


def get_team(user):  # TODO: Move to utils
    return Team.objects.filter(user__exact=user)[0]


def get_submissions(team):  # TODO: Move to utils
    return Submission.objects.filter(team__exact=team)


def get_result(id_number):  # TODO: Move to utils
    return Result.objects.filter(api_id__exact=id_number)


def index(request, params={}):
    return render(request, 'submission/index.html', params)


def submit(request):
    if not request.user.is_authenticated():
        return index(request)

    if request.POST:
        code = request.POST.get('source_code')
        team = get_team(request.user)
        id_number = submit_code(code, team)
        return my_results(request, message='Your code has been sent!')

    submission_end = time.localtime() > SUBMISSION_DEADLINE

    return render(request, 'submission/submit.html', {'submission_end': submission_end})


def my_results(request, message=''):
    if not request.user.is_authenticated():
        return index(request)

    params = {'submissions': [], 'message': message}
    team = get_team(request.user)
    submissions = get_submissions(team)

    for submission in submissions:
        in_db = False
        result = get_result(submission.api_id)
        result_string = ''
        if len(result) == 0:
            result_string = fetch_status(submission.api_id)
        else:
            in_db = True
            result_string = result[0].result
        params["submissions"].append(
            {
                "id": submission.api_id,
                "results": eval(str(result_string)),
            }
        )

        s = str(result_string).replace("{u'", "{'").replace(" u'", "'")
        d = eval(s)
        passed = False
        if not ('processing' in d or 'error' in d or 'timed_out' in d):
            if not in_db:
                result_in_db = Result()
                result_in_db.api_id = submission.api_id
                result_in_db.result = str(result_string)
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
