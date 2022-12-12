'''
This is a "hello world" flask webpage.
During the last 2 weeks of class,
we will be modifying this file to demonstrate all of flask's capabilities.
This file will also serve as "starter code" for your Project 5 Twitter webpage.

NOTE:
the module flask is not built-in to python,
so you must run pip install in order to get it.
After doing do, this file should "just work".
'''
import sqlite3,json
from flask import Flask, render_template, request, make_response, redirect, url_for
from datetime import datetime

from flask_babel import Babel, gettext 
app = Flask(__name__) #creates an app for us
app.config['BABEL_DEFAULT_LOCALE'] ='es'
babel = Babel(app)

con = sqlite3con = sqlite3.connect('twitter_clone.db')
cur = con.cursor()
# args.db_file = 'twitter_clone.db'
import argparse
parser = argparse.ArgumentParser(description='Create a database for the twitter project')
parser.add_argument('--db_file', default='twitter_clone.db')
args = parser.parse_args()

from werkzeug.security import generate_password_hash, check_password_hash

def print_debug_info():
    # Get method
    print('request.args.get("username")=', request.args.get('username'))
    print('request.args.get("password")=', request.args.get('password'))
    # Post Method 
    print('request.form.get("username")=', request.form.get('username'))
    print('request.form.get("password")=', request.form.get('password'))
    # Cookies
    print('request.cookies.get("username")=', request.cookies.get('username'))
    print('request.cookies.get("password")=', request.cookies.get('password'))

@babel.localeselector
def get_locale():
    return 'en'
   # request.accept_languages.best_match(['en', 'el'])

# class id(args.db_file): 
#     # ...

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)


@app.route('/') #index page
def root():

    # connect to the database
    con = sqlite3.connect(args.db_file)
    # construct messages,
    # which is a list of dictionaries,
    # where each dictionary contains the information about a message
    messages = []

    username=request.cookies.get('username')
    password=request.cookies.get('password')
    good_credentials=are_credentials_good(username,password)
    print('good_credentials=', good_credentials)

    sql = """
    SELECT sender_id,message,created_at
    FROM messages
    ORDER BY created_at DESC; 
    """
    cur_messages = con.cursor()
    cur_messages.execute(sql)
    for row_messages in cur_messages.fetchall():

        # convert sender_id into a username
        sql="""
        SELECT username,age
        FROM users
        WHERE id=?;
        """
        cur_users = con.cursor()
        cur_users.execute(sql, [row_messages[0]])
        for row_users in cur_users.fetchall():
            pass

        # build the message dictionary
        messages.append({
            'message': row_messages[1],
            'username': row_users[0],
            'created_at': row_messages[2],
            'profpic':'https://robohash.org/' + row_users[0],
            'age':row_users[1],
            })
    # render the jinja2 template and pass the result to firefox
    return render_template('root.html', messages=messages, logged_in=good_credentials)

def are_credentials_good(username,password):
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    username=username
    sql = """
    SELECT password FROM users where username= ?;
    """
    cur.execute(sql,[username])
    for row in cur.fetchall():
        if password == row[0]:
            return True
        else:
            return False 
        
    # if username=='haxor' and password=='1337':
    #     return True
    # else:
    #     return False

@app.route('/home.json')
def home_json():
    con = sqlite3.connect(args.db_file)
    cur = con.cursor()
    cur.execute('''
        SELECT sender_id, message, created_at, id from messages;
    ''')
    rows = cur.fetchall()
    messages = []
    for row in rows:
        messages.append({'username': row[0], 'text': row[1], 'created_at':row[2], 'id':row[3]})
    messages.reverse()

    return json.dumps(messages)

@app.route('/login', methods=['GET', 'POST'])
def login():
    print_debug_info()
    username=request.form.get('username')
    password=request.form.get('password')
    print("username=",username)
    print("password=",password)

    good_credentials=are_credentials_good(username,password)
    print('good_credentials=',good_credentials)

    if username is None:
        return render_template('login.html', bad_credentials=False)
    else:
        if not good_credentials:
            return render_template('login.html', bad_credentials=True)
        else:

            #If we get here then we are logged in, they typed the correct information
            
            #return 'login successful'
            response = make_response(redirect(url_for('root')))
            response.set_cookie('username', username)
            response.set_cookie('password', password)
            return response

@app.route('/logout')
def logout():
    response = make_response(render_template('logout.html'))
    response.delete_cookie('username')
    response.delete_cookie('password')
    return response

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    username=request.form.get('username')
    password=request.form.get('password')
    password1=request.form.get('password1')
    age=request.form.get('age')
    print(username, password, password1, age)
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    sql = """
    INSERT INTO users (username, password, age) VALUES (?, ?, ?);
    """
    if username:
            
        if password==password1:
            try:
                cur.execute(sql, [username, password, age])
                con.commit()
                response = make_response(redirect(url_for('root')))
                response.set_cookie('username', username)
                response.set_cookie('password', password)
                return response
            except:
                return render_template('create_user.html', usercreated= False, error= True )
        else:
            return render_template('create_user.html', usercreated= False, typo=True)
    else:
        return render_template('create_user.html', usercreated= False, error= False)

    
    
@app.route('/create_message', methods=['get', 'post'])
def create_message():
    username=request.cookies.get('username')
    password=request.cookies.get('password')
    good_credentials=are_credentials_good(username,password)
    print('good_credentials=', good_credentials)
    if(request.cookies.get('username') and request.cookies.get('password')):
        if request.form.get('newMessage'):
            con = sqlite3.connect(args.db_file)
            cur = con.cursor()
            cur.execute('''
                INSERT INTO messages (sender_id, message) values (?, ?);
            ''', (request.cookies.get('username'), request.form.get('newMessage')))
            con.commit()
            return make_response(render_template('create_message.html', created=True, logged_in= good_credentials, username=request.cookies.get('username'), password=request.cookies.get('password')))
        else:
            return make_response(render_template('create_message.html', created=False, logged_in= good_credentials, username=request.cookies.get('username'), password=request.cookies.get('password')))
    else:
        return login()


@app.route('/search_message', methods=['POST', 'GET'])
def search_message():
    username=request.cookies.get('username')
    password=request.cookies.get('password')
    good_credentials=are_credentials_good(username,password)
    print('good_credentials=', good_credentials)
    if request.form.get('search'):
        con = sqlite3.connect(args.db_file) 
        cur = con.cursor()
        cur.execute('''
            SELECT users.username, messages.message, messages.created_at, messages.id from messages join users ON messages.sender_id=users.id;
        ''')
        rows = cur.fetchall()
        messages = []
        for row in rows:
            if request.form.get('search') in row[1]:
                messages.append({'username': row[0], 'text': row[1], 'created_at':row[2], 'id':row[3]})
        messages.reverse()
        return render_template('search_message.html',logged_in= good_credentials, messages=messages, username=request.cookies.get('username'), password=request.cookies.get('password'))
    else:
        return render_template('search_message.html', logged_in= good_credentials, default=True, username=request.cookies.get('username'), password=request.cookies.get('password'))

@app.route('/change_password/<username>', methods=['post', 'get'])
def change_password(username):
    username=request.cookies.get('username')
    password=request.cookies.get('password')
    good_credentials=are_credentials_good(username,password)
    print('good_credentials=', good_credentials)
    if request.form.get('oldPassword'):
        if request.cookies.get('username') == username:
            con = sqlite3.connect(args.db_file) 
            cur = con.cursor()
            cur.execute('''
                SELECT password from users where username=?;
            ''', (username,))
            rows = cur.fetchall()
            oldPassword = rows[0][0]
            
            if request.form.get('oldPassword') == oldPassword:
                if request.form.get('password1') == request.form.get('password2'):
                    cur.execute('''
                        UPDATE users
                        SET password = ?
                        WHERE username = ?
                    ''', (request.form.get('password1'), request.cookies.get('username')))
                    con.commit()
                    return make_response(render_template('change_password.html', allGood=True,logged_in= good_credentials, username=request.cookies.get('username'), password=request.cookies.get('password')))
                else: 
                    return make_response(render_template('change_password.html', logged_in= good_credentials, repeatPass=True, username=request.cookies.get('username'), password=request.cookies.get('password')))
            else: 
                return make_response(render_template('change_password.html', logged_in= good_credentials, wrongPass=True, username=request.cookies.get('username'), password=request.cookies.get('password')))
        else: 
            return make_response(render_template('change_password.html', logged_in= good_credentials, not_your_username=True, username=request.cookies.get('username'), password=request.cookies.get('password')))
    else: return make_response(render_template('change_password.html', logged_in= good_credentials,username=request.cookies.get('username'), password=request.cookies.get('password')))

@app.route('/user')
def user():
    username=request.cookies.get('username')
    password=request.cookies.get('password')
    good_credentials=are_credentials_good(username,password)
    print('good_credentials=', good_credentials)
    if(request.cookies.get('username') and request.cookies.get('password')):
        con = sqlite3.connect(args.db_file)
        cur = con.cursor()
        cur.execute('''
            SELECT message, created_at, id from messages where sender_id=?;
        ''', (request.cookies.get('username'),))
        rows = cur.fetchall()
        messages = []
        for row in rows:
            messages.append({'text': row[0], 'created_at': row[1], 'id':row[2]})
        messages.reverse()
        return make_response(render_template('user.html', logged_in= good_credentials, messages=messages, username=request.cookies.get('username'), password=request.cookies.get('password')))
    else: 
        return login()

@app.route('/delete_account/<username>')
def delete_account(username):
    username=request.cookies.get('username')
    password=request.cookies.get('password')
    good_credentials=are_credentials_good(username,password)
    print('good_credentials=', good_credentials)
    if request.cookies.get('username') == username:
        con = sqlite3.connect(args.db_file) 
        cur = con.cursor()
        cur.execute('''
            DELETE from users where username=?;
        ''', (username,))
        con.commit()
        return make_response(render_template('delete_account.html', not_your_username=False, username=request.cookies.get('username'), password=request.cookies.get('password')))
    else:
        return make_response(render_template('delete_account.html', not_your_username=True, username=request.cookies.get('username'), password=request.cookies.get('password')))
'''@app.route('/static')s
def create_static():
    return render_template('static')'''

@app.route('/edit_message/<id>', methods=['POST', 'GET'])
def edit_message(id):
    if request.form.get('newMessage'):
        con = sqlite3.connect(args.db_file) 
        cur = con.cursor()
        cur.execute('''
            SELECT sender_id, message from messages where id=?;
        ''', (id,))
        rows = cur.fetchall()
        if rows[0][0] == request.cookies.get('username'):
            cur.execute('''
                UPDATE messages
                SET message = ?
                WHERE id = ?
            ''', (request.form.get('newMessage'),id))
            con.commit()
            return make_response(render_template('edit_message.html',allGood=True, id=id, username=request.cookies.get('username'), password=request.cookies.get('password')))
        else:
            return make_response(render_template('edit_message.html',not_your=True, id=id, username=request.cookies.get('username'), password=request.cookies.get('password')))
    else:
        return make_response(render_template('edit_message.html',default=True, id=id, username=request.cookies.get('username'), password=request.cookies.get('password')))

import praw
import random
import time

# FIXME:
# copy your generate_comment function from the madlibs assignment here
# madlibs = [
#     "Senator Bernie Sanders has enjoyed a [REMARKABLY] long career as the [ULTIMATE] political outsider. His signature message of income [INEQUALITY], delivered with a metronomic, almost numbing consistency, has often seemed like the [ONLY] thing [ONE] needed to know about him—that is, until he surged to the forefront of the 2020 Democratic field.",
#     "On October 23, 1971, at a [MEETING] in Vermont of the [SMALL], anti-war Liberty Union Party, Sanders, 30, raised his hand to run for U.S. Senate. He ran on the Liberty Union ticket for Senate in a [SPECIAL] election in [EARLY] 1972, and for governor later that year, and for Senate again in 1974, and for governor again in 1976. He never [GOT] more than 6 percent of the vote.",
#     "He [STARTED] a business [PRODUCING] low-budget filmstrips about Vermont and New England history that he sold to schools. He [MADE] a 30-minute documentary on Eugene Debs, a [PROMINENT] labor organizer in the early 1900s and the five-time presidential candidate of the Socialist Party of America—whom Sanders has [CITED] as a hero.",
#     "Sanders [PROPOSES] a $16.3tn (£12.5tn) Green New Deal that he [SAYS] would create 20 million jobs and pay for itself over 15 years, including through $3tn of taxes on oil companies. Sanders [SUPPORTS] the environment and wants to adopt [LEGISLATION] to [PROTECT] it",
#     "With an anti-establishment [STYLE] that has [CHANGED] little over five decades, Mr. Sanders has attracted a [LOYAL] cadre of fans. He often boasts, correctly, that some of his agenda items once [CONSIDERED] radical — “Medicare for all,” a $15 minimum wage, tuition-free public college — have [NOW] been embraced by many Democrats."
#     "Bernie Sanders is a [GREAT] [OLD] [MAN]. [EVERYBODY] [LOVES] Bernie Sanders. "
#     ]
# replacements = {
#     'REMARKABLY' : ['exceptionally', 'remarkably'],
#     'ULTIMATE' : ['absolute', 'ultimate'],
#     'INEQUALITY' : ['inequity', 'inequality', 'disproportion'],
#     'ONLY' : ['sole', 'only', 'single'],
#     'ONE' : ['someone', 'somebody', 'anoyone'],
#     'MEETING'  : ['assembly', 'conference', 'gathering'],
#     'SMALL' : ['little', 'small-scale', 'tiny'],
#     'SPECIAL' : ['particular', 'exceptional'],
#     'EARLY' : ['the beginning of', 'early'],
#     'GOT' : ['got', 'received'],
#     'STARTED' : ['initiated', 'started', 'established'],
#     'PRODUCING' : ['creating', 'producing'],
#     'MADE' : ['created', 'made', 'produced'],
#     'PROMINENT' : ['eminent', 'important', 'prominent'],
#     'CITED' : ['mentiioned', 'presented', 'cited'],
#     'PROPOSES' : ['proposes', 'suggests' 'offers'],
#     'SAYS' : ['highlights','mentions' 'says'],
#     'SUPPORTS' : ['helps', 'assists' 'supports'],
#     'LEGISLATION' : ['law', 'legislation', 'code'],
#     'PROTECT' : ['safeguard', 'save', 'protect'],
#     'STYLE' : ['way', 'style', 'methodology'],
#     'CHANGED': ['altered', 'transformed', 'changed'],
#     'LOYAL' : ['devoted', 'faithful', 'loyal'],
#     'CONSIDERED': ['perceived', 'considered'],
#     'NOW': ['currently', 'now'],
#     'GREAT': ['great', 'amazing', 'spectacular'],
#     'OLD': ['aged', 'senior', 'elder'],
#     'MAN': ['person', 'human', 'man'],
#     'EVERYBODY':['everyone', 'all people', 'anybody'],
#     'LOVES': ['adores', 'loves']}

# def generate_comment():
#     madlib = random.choice(madlibs)
#     for replacement in replacements.keys():
#         madlib = madlib.replace('['+replacement+']', random.choice(replacements[replacement]))
#     return madlib 

# for num in range(200):
#     con = sqlite3.connect(args.db_file)
#     cur = con.cursor()
#     username = 'rawaya'+str(num)
#     password = 'rawaya'+str(num)
#     age = str(num)
#     sql = """
#     INSERT INTO users (username, password, age) VALUES (?, ?, ?);
#     """
#     cur.execute(sql, [username, password, age])
#     con.commit()

# for num in range(200):
    
#     con = sqlite3.connect(args.db_file)
#     cur = con.cursor()
#     username = 'rawaya'+str(num)

#     sql =  """
#     Select id from USERS where username = ?
#     """
#     cur.execute(sql ,[username])
#     con.commit()
#     for row in cur.fetchall():
#         sender_id = row[0]

#     for num in range(200):
#         time_stamp = datetime.now()
#         sender_id = sender_id
#         message = generate_comment()
#         sql= """
#         INSERT INTO messages (sender_id, message, created_at) values (?, ?, ?);
#         """
#         cur.execute(sql, [sender_id, message, time_stamp.strftime("%Y-%m-%d %H:%M:%S") ]) 
#         con.commit()
if __name__ =="__main__":
    app.run(host='0.0.0.0')
