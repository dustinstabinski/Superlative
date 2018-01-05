import json
import webbrowser
import requests
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
from your_app_data import APP_ID, APP_SECRET


# Global facebook_session variable, needed for handling FB access below
facebook_session = False

# Function to make a request to Facebook provided.
# Reference: https://requests-oauthlib.readthedocs.io/en/latest/examples/facebook.html
def makeFacebookRequest(baseURL, params = {}):
    global facebook_session
    if not facebook_session:
        # OAuth endpoints given in the Facebook API documentation
        authorization_base_url = 'https://www.facebook.com/dialog/oauth'
        token_url = 'https://graph.facebook.com/oauth/access_token'
        redirect_uri = 'https://www.programsinformationpeople.org/runestone/oauth'

        scope = ['user_posts','pages_messaging','user_managed_groups','user_status','user_likes']
        facebook = OAuth2Session(APP_ID, redirect_uri=redirect_uri, scope=scope)
        facebook_session = facebook_compliance_fix(facebook)

        authorization_url, state = facebook_session.authorization_url(authorization_base_url)
        print('Opening browser to {} for authorization'.format(authorization_url))
        webbrowser.open(authorization_url)

        redirect_response = input('Paste the full redirect URL here: ')
        facebook_session.fetch_token(token_url, client_secret=APP_SECRET, authorization_response=redirect_response.strip())

    return facebook_session.get(baseURL, params=params)
#________________________________________________________________________________
CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except:
    CACHE_DICTION = {}
def getWithCaching(url, params={}):
    req = requests.Request(method = 'GET', url = url, params = sorted(params.items()))
    prepped = req.prepare()
    fullURL = prepped.url
    if fullURL not in CACHE_DICTION:
        response = requests.Session().send(prepped)
        CACHE_DICTION[fullURL] = response.text
        cache_file = open(CACHE_FNAME, 'w')
        cache_file.write(json.dumps(CACHE_DICTION))
        cache_file.close()
    return CACHE_DICTION[fullURL]
#__________________________________________________________________________________________


class Post():
    def __init__(self, post_dict = {}):
        if 'likes' in post_dict:
            self.likes = []
            likedata = post_dict['likes']
            while(True):
                try:
                    for c in likedata['data']:
                        self.likes.append(c)
                    likedata = json.loads((makeFacebookRequest(likedata['paging']['next'])).text)
                except KeyError:
                    break
        else:
            self.likes = []
        if 'comments' in post_dict:
            self.comments = []
            comdata = post_dict['comments']
            while(True):
                try:
                    for c in comdata['data']:
                        self.comments.append(c)
                    comdata = json.loads((makeFacebookRequest(comdata['paging']['next'])).text)
                except KeyError:
                    break
        else:
            self.comments = []
        if 'message' in post_dict:
            self.message = post_dict['message']
        self.data = post_dict
    def num_likes(self):
        return len(self.likes)

#_________________________________________________________________________________________________________________________________

post_inst = []
mainurl = 'https://graph.facebook.com/me/feed'
while(True):
    try:
        response1 = makeFacebookRequest(mainurl, params={'fields': 'likes,comments,message'})
        getWithCaching(mainurl, params={'fields': 'likes,comments,message'})
        respy1 = json.loads(response1.text)
        data = respy1['data']
        for c in data:
            post_inst.append(Post(c))
        mainurl = respy1['paging']['next']
    except KeyError:
        break
#_________________________________________________________________________________________________________________________________
def who_likes(post):
    return [c['name'] for c in post.likes]

list_of_friends = [who_likes(c) for c in post_inst]
one_list = []
for c in list_of_friends:
    one_list.extend(c)
like_dict = {}
for c in one_list:
    if c not in like_dict:
        like_dict[c] = 1
    else:
        like_dict[c] += 1
sorted_like_dict = sorted(like_dict, key= lambda x: like_dict[x], reverse = True)
#_______________________________________________________________________________________________________________________________________
def who_comments(post):
    return [c['from']['name'] for c in post.comments if 'from' in c]
list_of_com_friends = [who_comments(c) for c in post_inst]
one_list = []
for c in list_of_com_friends:
    if len(c) > 0:
        one_list.extend(c)
com_dict = {}
for c in one_list:
    if c not in com_dict:
        com_dict[c] = 1
    else:
        com_dict[c] += 1
sorted_com_dict = sorted(com_dict, key= lambda x: com_dict[x], reverse =True)
#_______________________________________________________________________________________________________________________________________
sort_like_list = sorted(post_inst, key=lambda x: len(x.likes), reverse=True)
sort_com_list = sorted(post_inst, key =lambda x: len(x.comments), reverse=True)
post_like_dict = {}
for c in sort_like_list:
    post_like_dict[c] = len(c.likes)

#____________________________________________________________________________________________________________________________________
sort_message_like_list = [c.message for c in sort_like_list if 'message' in c.data]
sort_message_com_list = [c.message for c in sort_com_list if 'message' in c.data]


#_____________________________________________________________________________________________________________________________________________________

#_________________________________________________________________________________________________________________________________________________________
def Choice1():
    func_string_1 = '''
    Would you like to view the list? (Enter yes or no)

    '''
    func_string_2 = '''
    Would you like to view more of the list (Enter yes or no)

    '''
    input_1 = ''
    counter = 0
    while input_1 != 'no':
        input_1 = input(func_string_1)
        if input_1 == 'yes':
            print('''
    It looks like {} (with {} likes) and {} (with {} likes) seem to really like to like the activity on your feed! Here’s a full list!

    {}'''.format(sorted_like_dict[0],like_dict[sorted_like_dict[0]], sorted_like_dict[1], like_dict[sorted_like_dict[1]], sorted_like_dict[(0+counter):(4+counter)]))
            counter = counter + 4
            func_string_1 = func_string_2
        elif input_1 == 'no':
            return('''
    Ok.
    ''')
        else:
            print('''
    I don't understand. Enter yes or no.

    ''')

def Choice2():
    func_string_1 = '''
    Would you like to view the list? (Enter yes or no)

    '''
    func_string_2 = '''
    Would you like to view more of the list (Enter yes or no)

    '''
    input_2 = ''
    counter2 = 0
    while input_2 != 'no':
        input_2 = input(func_string_1)
        if input_2 == 'yes':
            print('''
    It looks like {} (with {} comments) and {} (with {} comments) seem to really like to comment on the activity on your feed! Here’s a full list!

    {}'''.format(sorted_com_dict[0],com_dict[sorted_com_dict[0]], sorted_com_dict[1], com_dict[sorted_com_dict[1]], sorted_com_dict[(0+counter2):(4+counter2)]))
            counter2 = counter2 + 4
            func_string_1 = func_string_2
        elif input_2 == 'no':
            return('''
    Ok.
    ''')
        else:
            print('''
    I don't understand. Enter yes or no.

    ''')


def Choice3():
    func_string_1 = '''
    Would you like to view the list? (Enter yes or no)

    '''
    func_string_2 = '''
    Would you like to view more of the list (Enter yes or no)

    '''
    input_3 = ''
    counter3 = 0
    while input_3 != 'no':
        input_3 = input(func_string_1)
        if input_3 == 'yes':
            print('''
    Here is a list of your most popular posts on your feed sorted by the amount of likes.

    {}'''.format(sort_message_like_list[(0 + counter3):(4 + counter3)]))
            counter3 = counter3 + 4
            func_string_1 = func_string_2
        elif input_3 == 'no':
            return('''
        Ok.
            ''')
        else:
            print('''
        I don't understand. Enter yes or no.

        ''')

def Choice4():
    func_string_1 = '''
    Would you like to view the list? (Enter yes or no)

    '''
    func_string_2 = '''
    Would you like to view more of the list (Enter yes or no)

    '''
    input_4 = ''
    counter4 = 0
    while input_4 != 'no':
        input_4 = input(func_string_1)
        if input_4 == 'yes':
            print('''
    Here is a list of your most popular posts on your feed sorted by the amount of comments.

    {}'''.format(sort_message_com_list[(0 + counter4):(4 + counter4)]))
            counter4 = counter4 + 4
            func_string_1 = func_string_2
        elif input_4 == 'no':
            return('''
    Ok.
            ''')
        else:
            print('''
    I don't understand. Enter yes or no.

            ''')

#_____________________________________________________________________________________________________________________________________________________________
string = '''
    Welcome to the Facebook Superlative and Popularity Application. To get started, please select one of the following options (To select, just type one of the following numbers in). When you are done, type 'quit'.

    1. Find out which of your friends liked the most amount of posts on your feed! This will give you a list of your friends sorted by how active they are on your feed in terms of likes.

    2. Find out which of your friends commented on the most amount of posts on your feed! This will give you a list of your friends sorted by how active they are on your feed in terms of comments.

    3. Find out which of your posts received the most likes. This option will present you with a list of your posts sorted by how many likes were received on each given post.

    4. Find out which of your posts received the most comments. This option will present you with a list of your posts sorted by how many comments were received on each given post.

    5. Clear cache.

    '''
string2 = '''
    What else would you like to see?

    1. Find out which of your friends liked the most amount of posts on your feed! This will give you a list of your friends sorted by how active they are on your feed in terms of likes.

    2. Find out which of your friends commented on the most amount of posts on your feed! This will give you a list of your friends sorted by how active they are on your feed in terms of comments.

    3. Find out which of your posts received the most likes. This option will present you with a list of your posts sorted by how many likes were received on each given post.

    4. Find out which of your posts received the most comments. This option will present you with a list of your posts sorted by how many comments were received on each given post.

    5. Clear cache.

    '''
string3 = '''
    Sorry, I didn't understand that. Try again.

    1. Find out which of your friends liked the most amount of posts on your feed! This will give you a list of your friends sorted by how active they are on your feed in terms of likes.

    2. Find out which of your friends commented on the most amount of posts on your feed! This will give you a list of your friends sorted by how active they are on your feed in terms of comments.

    3. Find out which of your posts received the most likes. This option will present you with a list of your posts sorted by how many likes were received on each given post.

    4. Find out which of your posts received the most comments. This option will present you with a list of your posts sorted by how many comments were received on each given post.

    5. Clear cache.

    '''
x = ''
while x != "quit":
    x = input(string)
    if x == "1":
        print(Choice1())
        string = string2
    elif x == "2":
        print(Choice2())
        string = string2
    elif x =="3":
        print(Choice3())
        string = string2
    elif x == "4":
        print(Choice4())
        string = string2
    elif x =="5":
        print('''
    Cache has been cleared.
    ''')
        CACHE_DICTION = {}
        cache_file = open(CACHE_FNAME, 'w')
        cache_file.write(json.dumps(CACHE_DICTION))
        cache_file.close()
    elif x=='quit':
        print('''
    Goodbye!
    ''')
    else:
        print('''
    Sorry, I didn't understand that!
    ''')
        string = string2
#______________________________________________________________________________________________________________________________________
