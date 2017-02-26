from flask import Flask, redirect, url_for, render_template, session, g, request, jsonify
import sqlite3
import random
import string
import os
import uuid
import ConfigParser
import logging
from logging.handlers import RotatingFileHandler
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from urlparse import urlparse


app = Flask(__name__)
app.secret_key = 'z\xe1^a\xa5~J5\xd7\xa4Pk\xb0c\xac\x0e\xfb\xda\xff\x1d\x98\xd6i\x81'



############################################
##               DATABASE                 ##
############################################

db_location = 'var/reddit.db'

def get_db():
  db=getattr(g, 'db', None)
  if db is None:
    db = sqlite3.connect(db_location)
    g.db = db
  return db

@app.teardown_appcontext
def close_db_connection(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()

def init_db():
  with app.app_context():
    db = get_db()
    with app.open_resource('var/schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
      db.commit()


############################################
##              Error pages               ##
############################################


@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
  return render_template('500.html'), 500




############################################
##           Login/Registration           ##
############################################


##------ Registration page ------##
@app.route('/register')
def register():
  if 'user_id' not in session:
    return render_template('register.html'), 200

  #: if user is already logged in, return to root
  return redirect(url_for('root')), 302


##------ Register new user ------##
@app.route('/register/new', methods = ['POST', 'GET'])
def register_user():

  #: check if request method is POST
  if request.method == 'POST':
    #: check if passwords match
    if request.form['password'] == request.form['confirm_password']:
      try:
        #: generate a unique identifier for the user_id
        user_id = str(uuid.uuid4())

        #: request user input data
        username = request.form['username']
        password = request.form['password']

        #: hash the password
        pw_hashed = generate_password_hash(password)

        #: generate timestamp
        created_on = datetime.utcnow()

        #: insert into the database
        with sqlite3.connect(db_location) as con:
          cursor = con.cursor()
          cursor.execute("INSERT INTO users(user_id,username,password,created_on) VALUES(?,?,?,?)",(user_id,username,pw_hashed,created_on))
          con.commit()
          message = 'registration_success'

      #: if there is an error create an error message
      except:
        con.rollback()
        message = 'registration_error'

      #: if registration is successful, redirect to the login page with success message.
      finally:
        if message == 'registration_success':
          return render_template('login.html', message = message)
        else:
          return render_template('register.html', message = message)
        con.close()

      #: set message if passwords match
      message = 'password_match'
    else:
      message = 'password_error'
      return render_template('register.html', message = message)

  else:
    #: if request method is not 'POST', set log data and redirect to registration page.
    app.logger.info("User attempted to directly access '%s' without using the registration form.", url_for('register_user'))
    return redirect(url_for('register')), 302

##------ Login ------##
@app.route('/login', methods = ['GET', 'POST'])
def login():
  if 'user_id' not in session:
    if request.method == 'POST':
      #: request input data
      username = request.form['username']
      password = request.form['password']

      #: connect to database
      con = sqlite3.connect(db_location)
      cursor = con.cursor()
      cursor.execute("SELECT * FROM users WHERE username=?",(username,) )

      user_exists = cursor.fetchall()

      if user_exists:
        for row in user_exists:
          #: if user exists, check hashed pw from database matches pw entered by user
          pw_hashed = row[2]
          pw_check = check_password_hash(pw_hashed, password)
          if pw_check:
            #: if passwords match, set sessions and redirect to root.
            session['user_id'] = row[0]
            session['username'] = row[1]

            #: check if there is a target for redirect e.g. if someone logs in from another page they will be redirected back to that page
            if 'target' in session:
              target = session['target']
              return redirect(url_for(target)), 302
            #: if no target, log in as usual and redirect to the frontpage
            else:
              return redirect(url_for('root')), 302
          else:
            #: log if user enters incorrect password.
            app.logger.info("Incorrect password entered by user '%s'. Route: '%s'", username, url_for('login'))
            message = 'password_hash_error'
            #: if password is incorrect, return to login page with error message.
            return render_template('login.html', message = message), 401
      else:
        #: if user does not exist, return to login page with error message.
        message = 'user_exists_error'
        return render_template('login.html', message = message), 401
      con.close()
    #: if method is not 'POST' redirect to login page.
    return render_template('login.html'), 200

  #: log if user attempts to access login page while already logged in.
  app.logger.info("User '%s' attemped to access log in page while already logged in.", session['username'])
  return redirect(url_for('root')), 302


##------ Logout ------##
@app.route('/logout')
def logout():
  #: kill the session
  session.pop('user_id', None)
  session.pop('username', None)
  return redirect(url_for('root'))





############################################
##              Frontpage                 ##
############################################

##------ Frontpage (root) ------##
@app.route('/')
def root():
  if 'subreddit' in session:
    session.pop('subreddit', None)
    session.pop('subreddit_id', None)
  if 'username' in session:
    username = session['username']
  else:
    username = 'null'
  con = sqlite3.connect(db_location)
  con.row_factory = sqlite3.Row
  cursor = con.cursor()

  #: get posts ordered by newest first
  cursor.execute("SELECT * FROM posts ORDER BY post_timestamp DESC")
  new_posts = cursor.fetchall()

  #: get links
  #cursor.execute("SELECT post_link FROM posts ORDER BY post_timestamp DESC")
  #get_links = cursor.fetchall()
  #for link in get_links:
  #  parse_link = urlparse(link)
  #  if parse_link.netloc=='www.youtube.com':
  #    youtube=='true'
  #  else:
  #    youtube=='false'

  #: get posts ordered by vote count
  cursor.execute("SELECT * FROM posts ORDER BY cast(post_votes as REAL) DESC")
  top_posts = cursor.fetchall()


  #: check posts upvoted by user
  cursor.execute("SELECT post_id FROM posts WHERE upvoted_by_user LIKE ? ORDER BY post_timestamp desc",('%'+username+'%',))
  upvoted_by_user = cursor.fetchall()


  #: check posts downvoted by user
  cursor.execute("SELECT post_id FROM posts WHERE downvoted_by_user LIKE ? ORDER BY post_timestamp desc",('%'+username+'%',))
  downvoted_by_user = cursor.fetchall()


  #: check posts upvoted by user ordered by top
  cursor.execute("SELECT post_id FROM posts WHERE upvoted_by_user LIKE ? ORDER BY cast(post_votes as REAL) desc",('%'+username+'%',))
  top_upvoted_by_user = cursor.fetchall()


  #: check posts downvoted by user ordered by top
  cursor.execute("SELECT post_id FROM posts WHERE downvoted_by_user LIKE ? ORDER BY cast(post_votes as REAL) desc",('%'+username+'%',))
  top_downvoted_by_user = cursor.fetchall()


  #return str(upvoted_by_user[1][0])
  return render_template('frontpage.html', new_posts = new_posts, top_posts = top_posts, upvoted_by_user = upvoted_by_user, downvoted_by_user = downvoted_by_user, top_upvoted_by_user = top_upvoted_by_user, top_downvoted_by_user = top_downvoted_by_user), 200




############################################
##              Subreddits                ##
############################################

##------ Subreddit ------##
@app.route('/r/<string:subreddit>')
@app.route('/r/<string:subreddit>/')
def subreddit(subreddit):
  if subreddit:

    if 'username' in session:
      username = session['username']
    else:
      username = 'null'

    #session['subreddit'] = subreddit

    con = sqlite3.connect(db_location)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()

    cursor.execute("SELECT * FROM subreddits WHERE subreddit_name=?",(subreddit, ))
    sub_exists = cursor.fetchall()

    #: get posts ordered by newest
    cursor.execute("SELECT * FROM posts WHERE related_subreddit_name=? ORDER BY post_timestamp desc",(subreddit, ))
    sub_posts_new = cursor.fetchall()

    #: get posts ordered by vote count
    cursor.execute("SELECT * FROM posts WHERE related_subreddit_name=? ORDER BY cast(post_votes as REAL) DESC",(subreddit, ))
    sub_posts_top = cursor.fetchall()

    #: get number of comments for each post
    cursor.execute("SELECT related_post_id FROM comments")
    comments_count = cursor.fetchall()

    #: check posts upvoted by user
    cursor.execute("SELECT post_id FROM posts WHERE upvoted_by_user LIKE ? AND related_subreddit_name=? ORDER BY post_timestamp desc",('%'+username+'%',subreddit))
    upvoted_by_user = cursor.fetchall()


    #: check posts downvoted by user
    cursor.execute("SELECT post_id FROM posts WHERE downvoted_by_user LIKE ? AND related_subreddit_name=? ORDER BY post_timestamp desc",('%'+username+'%',subreddit))
    downvoted_by_user = cursor.fetchall()

    #: check posts upvoted by user order by top
    cursor.execute("SELECT post_id FROM posts WHERE upvoted_by_user LIKE ? AND related_subreddit_name=? ORDER BY cast(post_votes as REAL) desc",('%'+username+'%',subreddit))
    top_upvoted_by_user = cursor.fetchall()


    #: check posts downvoted by user order by top
    cursor.execute("SELECT post_id FROM posts WHERE downvoted_by_user LIKE ? AND related_subreddit_name=? ORDER BY cast(post_votes as REAL) desc",('%'+username+'%',subreddit))
    top_downvoted_by_user = cursor.fetchall()


    #cursor.execute("SELECT post_timestamp FROM posts WHERE related_subreddit_name=?",(subreddit, ))
    #post_timestamps = cursor.fetchall()


    for row in sub_exists:
      session['subreddit'] = row["subreddit_name"]
      session['subreddit_id'] = row["subreddit_id"]

    now = str(datetime.utcnow())
    #for timestamp in post_timestamps:
      #: calculate time since post was made
      #now = str(datetime.utcnow())
      #post_timestamp = str(column["post_timestamp"])
    #post_timestamp = post_timestamps
      #timecalc = now - 9000
      #d = divmod(now-post_timestamp,86400) #days
      #h = divmod(d[1],3600) #hours
      #m = divmod(h[1],60) #minutes
      #s = m[1] #seconds
      #timesince = '%d days, %d hours, %d mins, %d seconds ago' % (d[0],h[0],m[0],s)
    #for post in post_timestamp:
    #for post_timestamp in post_timestamps:
      #datetimeFormat = "%Y-%m-%d %H:%M:%S.%f"
      #timesince = datetime.strptime(now, datetimeFormat) - datetime.strptime(str(post_timestamp[0]), datetimeFormat)




    if sub_exists:
      return render_template('subreddit.html', sub = sub_exists, sub_posts_new = sub_posts_new, sub_posts_top = sub_posts_top, comments_count = comments_count, upvoted_by_user = upvoted_by_user, downvoted_by_user = downvoted_by_user, top_upvoted_by_user = top_upvoted_by_user, top_downvoted_by_user = top_downvoted_by_user)
    else:
      return render_template('subreddit.html', error = subreddit)



##------ Subreddit list ------##
@app.route('/subreddits', methods = ['GET'])
def subreddit_list():

  #: show a list of all subreddits. possibly add search functionality with autocomplete.

  con = sqlite3.connect(db_location)
  con.row_factory = sqlite3.Row

  cursor = con.cursor()
  cursor.execute("SELECT * FROM subreddits ORDER BY subreddit_name asc")

  rows = cursor.fetchall()

  return render_template('subreddit_list.html', rows = rows)

#: if user doesn't enter a subreddit name, redirect to subreddit list
@app.route('/r/')
def r_redirect_slash():
  app.logger.info("User did not enter a subreddit. Route: '%s'.", url_for('r_redirect_slash'))
  return redirect(url_for('subreddit_list'))


##------ Subreddit Creation Page ------##
@app.route('/subreddits/create')
def subreddit_creation_form():
  if 'target' in session:
    session.pop('target', None)

  if 'user_id' in session:

    return render_template('create_subreddit.html')

  #: if user is not logged in, redirect to login page.
  else:
    session['target'] = "subreddit_creation_form"
    target=session['target']
    return redirect(url_for('login', target=target))


##------ Add Subreddit to database ------##
@app.route('/subreddits/create/confirm', methods = ['POST', 'GET'])
def create_subreddit():
  if 'user_id' in session:
    user_id = session['user_id']
    username = session['username']

    if request.method == 'POST':
      try:
        subreddit_id = str(uuid.uuid4())
        subreddit_name = request.form['subreddit_name']
        subreddit_title = request.form['subreddit_title']
        subreddit_desc = request.form['subreddit_desc']
        subreddit_sidebar = request.form['subreddit_sidebar']
        subreddit_created_on = datetime.utcnow()
        created_by_user = username

        with sqlite3.connect(db_location) as con:
          cursor = con.cursor()

          #: insert data
          cursor.execute("INSERT INTO subreddits(subreddit_id,subreddit_name,subreddit_title,subreddit_desc,subreddit_sidebar,subreddit_created_on,created_by_user) VALUES(?,?,?,?,?,?,?)",(subreddit_id,subreddit_name,subreddit_title,subreddit_desc,subreddit_sidebar,subreddit_created_on,created_by_user))

          con.commit()

          #: if successful
          message = "subreddit_created"

      except:
        con.rollback()
        #: if unsucessful
        message = "subreddit_error"

      finally:
        #: if successful, redirect to the newly created subreddit.
        return redirect(url_for('subreddit', subreddit=subreddit_name))

    else:
      #: if method is not POST, redirect to the subreddit creation form
      return redirect(url_for('subreddit_creation_form'))

  else:
    #: if no session is found, redirect to login page.
    return redirect(url_for('login'))



##########################################
##               POSTS                  ##
##########################################

@app.route('/submit', methods = ['GET'])
def submit_form():
  if 'user_id' in session:
    if 'subreddit' in session:
      sub_name = session['subreddit']
      sub_id = session['subreddit_id']
    else:
      sub_name=''
      sub_id=''

    if 'target' in session:
      session.pop('target', None)

    con = sqlite3.connect(db_location)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()

    cursor.execute("SELECT subreddit_name,subreddit_id FROM subreddits ORDER BY subreddit_name")

    subreddits = cursor.fetchall();

    return render_template('create_post.html', subreddits=subreddits, sub_name = sub_name, sub_id = sub_id)
    con.close()
  else:
    session['target'] = "submit_form"
    target = session['target']
    return redirect(url_for('login', target = target))



@app.route('/submit/post', methods = ['POST', 'GET'])
def submit_post():
  if 'user_id' in session:
    if 'subreddit' in session:
      session.pop('subreddit', None)
      session.pop('subreddit_id', None)
    if request.method == 'POST':
      try:
        post_id = '5'+''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
        related_subreddit_id = request.form['subreddit_id']
        related_subreddit_name = request.form['subreddit_name']
        related_user_id = session['username']
        post_type = request.form['post_type']

        #: parse url
        get_link = request.form['post_link']
        parse_link = urlparse(get_link)
        if parse_link.scheme=='':
          post_link = 'http://'+parse_link.geturl()
        else:
          post_link = parse_link.geturl()

        post_textarea = request.form['post_textarea']

        post_title = request.form['post_title']
        #: make a url-friendly title
        split_title = post_title.split()
        trim_title = split_title[:8]
        url_friendly_title = '_'.join(word for word in trim_title).lower()

        now = datetime.utcnow()
        post_timestamp = str(now.strftime("%d %b %Y at %H:%M"))
        #post_timestamp = str(datetime.utcnow())
        post_votes = '0'
        upvoted_by_user = ' '
        downvoted_by_user = ' '

        with sqlite3.connect(db_location) as con:
          cursor = con.cursor()

          cursor.execute("INSERT INTO posts(post_id,related_subreddit_id,related_subreddit_name,related_user_id,post_type,post_title,url_friendly_title,post_link,post_textarea,post_timestamp,post_votes,upvoted_by_user,downvoted_by_user) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(post_id,related_subreddit_id,related_subreddit_name,related_user_id,post_type,post_title,url_friendly_title,post_link,post_textarea,post_timestamp,post_votes,upvoted_by_user,downvoted_by_user) )

          con.commit()

          message = 'post_success'

      except:
        con.rollback()
        message = 'post_error'
        return redirect(url_for('submit_form'), message = message)

      finally:
        return redirect(url_for('comments_section', subreddit = related_subreddit_name, post_id = post_id, post_title = url_friendly_title))
        con.close()
    else:
      return redirect(url_for('submit_form'))


  else:
    return redirect(url_for('login'))


##------ Delete post ------##
@app.route('/delete/post', methods = ['POST'])
def delete_post():
  if 'username' in session:
    if request.method == 'POST':

      post_id = request.form['post_id']

      con = sqlite3.connect(db_location)
      con.row_factory = sqlite3.Row
      cursor = con.cursor()

      cursor.execute("DELETE FROM posts WHERE post_id=?",(post_id,))
      cursor.execute("DELETE FROM comments WHERE related_post_id=?",(post_id,))
      con.commit()

      message = 'post_deleted'

      return redirect(url_for('root'))




  return redirect(url_for('login'))



##------ Comments section ------##
@app.route('/r/<string:subreddit>/comments/<string:post_id>/<string:post_title>/')
def comments_section(subreddit, post_id, post_title):

  con = sqlite3.connect(db_location)
  con.row_factory = sqlite3.Row
  cursor = con.cursor()

  #: get comments related to post_id
  #cursor.execute("SELECT * FROM comments WHERE related_post_id=?",(post_id, ))
  #comments_list = cursor.fetchall()

  #: get subreddit data
  cursor.execute("SELECT * FROM subreddits WHERE subreddit_name=?",(subreddit, ))
  subreddit = cursor.fetchall()

  #: get all top level comments (direct replies to the post)
  cursor.execute("SELECT * FROM comments WHERE related_post_id=parent_id AND related_post_id=?",(post_id, ))
  top_level_comments = cursor.fetchall()

  #: get all comment replies
  cursor.execute("SELECT * FROM comments WHERE related_post_id != parent_id")
  comment_replies = cursor.fetchall()

  #: get post related to post_id
  cursor.execute("SELECT * FROM posts WHERE post_id=?",(post_id, ))
  post_details = cursor.fetchall()


  return render_template('comments.html', post_details = post_details, top_level_comments = top_level_comments, comment_replies = comment_replies, subreddit = subreddit)



##------ Comments form ------##
@app.route('/comment/post', methods = ['POST','GET'])
def add_comment():
  if 'user_id' in session:
    if request.method == 'POST':

      try:
        comment_id = str(uuid.uuid4())
        related_post_id = request.form['related_post_id']
        related_user_id = session['username']
        comment_level = '0'
        parent_id = request.form['related_post_id']
        now = datetime.utcnow()
        comment_timestamp = str(now.strftime("%d %b %Y at %H:%M"))
        comment_votes = '0'
        comment_text = request.form['comment_text']
        top_parent_id = 'n/a'

        # request hidden form data to help with redirection back to the current page if comment is posted successfully.
        subreddit = request.form['subreddit']
        post_id = request.form['related_post_id']
        post_title = request.form['post_title']

        with sqlite3.connect(db_location) as con:
          cursor = con.cursor()
          cursor.execute("INSERT INTO comments(comment_id,related_post_id,related_user_id,comment_level,parent_id,comment_timestamp,comment_votes,comment_text,top_parent_id) VALUES(?,?,?,?,?,?,?,?,?)",(comment_id,related_post_id,related_user_id,comment_level,parent_id,comment_timestamp,comment_votes,comment_text,top_parent_id) )
          con.commit()

          message = 'comment_success'

      except:
        con.rollback()
        message = 'comment_error'
        return 'error. redirect back to comments page'

      finally:

        #: return the user back to the current page with #anchor to current comment.
        return redirect(url_for('comments_section', subreddit = subreddit, post_id = post_id, post_title = post_title, _anchor = comment_id))

  else:
    return redirect(url_for('login'))


@app.route('/comment/reply', methods = ['POST','GET'])
def add_reply():
  if 'user_id' in session:
    if request.method == 'POST':

      try:
        comment_id = str(uuid.uuid4())
        related_post_id = request.form['related_post_id']
        related_user_id = session['username']
        comment_level = int(request.form['parent_level']) + 1
        parent_id = request.form['parent_id']
        now = datetime.utcnow()
        comment_timestamp = str(now.strftime("%d %b %Y at %H:%M"))
        comment_votes = '0'
        comment_text = request.form['reply_text']
        top_parent_id = request.form['top_parent_id']

        # request hidden form data to help with redirection back to the current page if comment is posted successfully.
        subreddit = request.form['subreddit']
        post_id = request.form['related_post_id']
        post_title = request.form['post_title']

        with sqlite3.connect(db_location) as con:
          cursor = con.cursor()
          cursor.execute("INSERT INTO comments(comment_id,related_post_id,related_user_id,comment_level,parent_id,comment_timestamp,comment_votes,comment_text,top_parent_id) VALUES(?,?,?,?,?,?,?,?,?)",(comment_id,related_post_id,related_user_id,comment_level,parent_id,comment_timestamp,comment_votes,comment_text,top_parent_id) )
          con.commit()

          message = 'comment_success'

      except:
        con.rollback()
        message = 'comment_error'
        return 'error. redirect back to comments page'

      finally:

        #: return the user back to the current page with #anchor to current comment.
        return redirect(url_for('comments_section', subreddit = subreddit, post_id = post_id, post_title = post_title, _anchor = comment_id))

  else:
    return redirect(url_for('login'))



###########################################
##                VOTING                 ##
###########################################

##------ Vote on posts ------##
@app.route('/post/vote', methods = ['POST'])
def vote_post():
  if 'user_id' in session:
    if request.method == 'POST':
      data = request.form['data']
      post_id = request.form['post_id']
      upvoted_by_user = request.form['upvoted_by_user']
      downvoted_by_user = request.form['downvoted_by_user']

      con = sqlite3.connect(db_location)
      con.row_factory = sqlite3.Row
      cursor = con.cursor()

      cursor.execute("UPDATE posts SET post_votes=? WHERE post_id=?",(data,post_id))
      con.commit()


#: store upvotes
      if upvoted_by_user != 'null':
        cursor.execute("SELECT upvoted_by_user FROM posts WHERE upvoted_by_user LIKE ? AND post_id=?",('%'+upvoted_by_user+'%',post_id,))
        check_upvotes = cursor.fetchall()


        #: if user is already in the list: #
        if check_upvotes:

          #: get list of users who have upvoted the post
          for users in check_upvotes:
            upvotes_list = users[0]

          upvotes_list_updated = upvotes_list.replace('-'+upvoted_by_user, "", 1)

          cursor.execute("UPDATE posts SET upvoted_by_user=? WHERE post_id=?", (upvotes_list_updated, post_id))
          con.commit()
        else :
          cursor.execute("SELECT upvoted_by_user FROM posts WHERE post_id=?", (post_id, ))
          post = cursor.fetchall()

          for p in post:
            upvotes_list = p[0]

          upvotes_list_updated = upvotes_list.replace(upvotes_list,upvotes_list+'-'+upvoted_by_user, 1)

          cursor.execute("UPDATE posts SET upvoted_by_user=? WHERE post_id=?", (upvotes_list_updated, post_id))
          con.commit()


#: store downvotes

      if downvoted_by_user != 'null':
        cursor.execute("SELECT downvoted_by_user FROM posts WHERE downvoted_by_user LIKE ? AND post_id=?",('%'+downvoted_by_user+'%',post_id,))
        check_downvotes = cursor.fetchall()


        #: if user is already in the list: #
        if check_downvotes:

          #: get list of users who have upvoted the post
          for users in check_downvotes:
            downvotes_list = users[0]

          downvotes_list_updated = downvotes_list.replace('-'+downvoted_by_user, "", 1)

          cursor.execute("UPDATE posts SET downvoted_by_user=? WHERE post_id=?", (downvotes_list_updated, post_id))
          con.commit()
        else :
          cursor.execute("SELECT downvoted_by_user FROM posts WHERE post_id=?", (post_id, ))
          post = cursor.fetchall()

          for p in post:
            downvotes_list = p[0]

          downvotes_list_updated = downvotes_list.replace(downvotes_list,downvotes_list+'-'+downvoted_by_user, 1)

          cursor.execute("UPDATE posts SET downvoted_by_user=? WHERE post_id=?", (downvotes_list_updated, post_id))
          con.commit()


      return data

    return 'error'
  else:
    return redirect(url_for('login'))

##------ Vote on comments ------##

#: code similar to the above but for comments.



##########################################
##             User Profiles            ##
##########################################

##------ User profile page ------##
@app.route('/user/<string:user>')
@app.route('/u/<string:user>')
def user(user):
  if 'username' in session:
    username = session['username']
  else:
    username = 'null'

  if user:

    #: connect to database
    con = sqlite3.connect(db_location)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()

    #: get data from users table
    cursor.execute("SELECT user_id, username, created_on FROM users WHERE username=?",(user, ))
    user_exists = cursor.fetchall()

    #: get posts by user
    cursor.execute("SELECT * FROM posts WHERE related_user_id=? ORDER BY post_timestamp desc",(user, ))
    user_posts = cursor.fetchall()

    #: get all posts
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()

    #: get comments by user
    cursor.execute("SELECT * FROM comments WHERE related_user_id=? ORDER BY comment_timestamp desc",(user, ))
    user_comments = cursor.fetchall()

    #: get subreddits created by user
    cursor.execute("SELECT * from subreddits WHERE created_by_user=?",(user, ))
    mod_subs = cursor.fetchall()


    #: check posts upvoted by user
    cursor.execute("SELECT post_id FROM posts WHERE upvoted_by_user LIKE ? ORDER BY post_timestamp desc",('%'+username+'%',))
    upvoted_by_user = cursor.fetchall()


    #: check posts downvoted by user
    cursor.execute("SELECT post_id FROM posts WHERE downvoted_by_user LIKE ? ORDER BY post_timestamp desc",('%'+username+'%',))
    downvoted_by_user = cursor.fetchall()

    #: check posts upvoted by user order by top
    cursor.execute("SELECT post_id FROM posts WHERE upvoted_by_user LIKE ? ORDER BY cast(post_votes as REAL) desc",('%'+username+'%',))
    top_upvoted_by_user = cursor.fetchall()


    #: check posts downvoted by user order by top
    cursor.execute("SELECT post_id FROM posts WHERE downvoted_by_user LIKE ? ORDER BY cast(post_votes as REAL) desc",('%'+username+'%',))
    top_downvoted_by_user = cursor.fetchall()


    if user_exists:

      if user_posts:
        #: if user has posts check if they moderate any subreddits, if so, pass the list of subreddits to the template.
        if user_posts and mod_subs:
          return render_template('user.html', user = user_exists, user_posts = user_posts, mod_subs = mod_subs, user_comments = user_comments, posts = posts, upvoted_by_user = upvoted_by_user, downvoted_by_user = downvoted_by_user)
        else:
          return render_template('user.html', user = user_exists, user_posts = user_posts, user_comments = user_comments, posts = posts, upvoted_by_user = upvoted_by_user, downvoted_by_user = downvoted_by_user)

      #: if user has no posts, render the blank user template
      else:
        return render_template('user.html', user = user_exists)


    #: if user doesn't exists, return error
    else:
      return render_template('user.html', error = user)





##------ Run the app ------##
if __name__ == "__main__":
  formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
  handler = RotatingFileHandler('var/loggingapp.log', maxBytes=10000, backupCount=5)
  handler.setLevel(logging.DEBUG)
  handler.setFormatter(formatter)
  app.logger.addHandler(handler)
  app.run(host='0.0.0.0', debug=True)
