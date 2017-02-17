import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db
import hashutils
import re


# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

# a list of movies that nobody should be allowed to watch
terrible_movies = [
    "Gigli",
    "Star Wars Episode 1: Attack of the Clones",
    "Paul Blart: Mall Cop 2",
    "Nine Lives"
]

# a list of pages that anyone is allowed to visit
# no login required to view these routes
allowed_routes = [
    "/login",
    "/logout",
    "/register"
]

class User(db.Model):
    username = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)


class Movie(db.Model):
    title = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    watched = db.BooleanProperty(required = True, default = False)
    rating = db.StringProperty()

class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.
        The other handlers inherit form this one.
    """

    def renderError(self, error_code):
        """ Sends an HTTP error code and a generic "oops!" message to the client. """

        self.error(error_code)
        self.response.write("Oops! Something went wrong.")

    def login_user(self, user):
        user_id = user.key().id()
        self.set_secure_cookie('user_id', str(user_id))

    def logout_user(self):
        self.set_secure_cookie('user_id', '')

    def set_secure_cookie(self, name, val):
        cookie_val = hash_utils.make_secure_val(val)
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        if cookie_val:
            return hashutils.check_secure_val(cookie_val)

    def get_user_by_name(self, username):
        user = db.GqQuery("SELECT * FROM User WHERE username = '%s'" % username)
        if user:
            return user.get()

    def initialize(self, *args, **kwargs):
        webapp2.Requesthandler.initialize(self, *args, **kwargs)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.get_by_id(int(uid))

        if not self.user and self.request.path not in allowed_routes:
            self.redirect('/login')


class Index(Handler):
    """ Handles requests coming in to '/' (the root of our site)
        e.g. www.flicklist.com/
    """

    def get(self):
        unwatched_movies = db.GqlQuery("SELECT * FROM Movie where watched = False")
        t = jinja_env.get_template("frontpage.html")
        content = t.render(
                        movies = unwatched_movies,
                        error = self.request.get("error"))
        self.response.write(content)

class AddMovie(Handler):
    """ Handles requests coming in to '/add'
        e.g. www.flicklist.com/add
    """

    def post(self):
        new_movie_title = self.request.get("new-movie")

        # if the user typed nothing at all, redirect and yell at them
        if (not new_movie_title) or (new_movie_title.strip() == ""):
            error = "Please specify the movie you want to add."
            self.redirect("/?error=" + cgi.escape(error))

        # if the user wants to add a terrible movie, redirect and yell at them
        if new_movie_title in terrible_movies:
            error = "Trust me, you don't want to add '{0}' to your Watchlist.".format(new_movie_title)
            self.redirect("/?error=" + cgi.escape(error, quote=True))

        # 'escape' the user's input so that if they typed HTML, it doesn't mess up our site
        new_movie_title_escaped = cgi.escape(new_movie_title, quote=True)

        # construct a movie object for the new movie
        movie = Movie(title = new_movie_title_escaped)
        movie.put()

        # render the confirmation message
        t = jinja_env.get_template("add-confirmation.html")
        content = t.render(movie = movie)
        self.response.write(content)


class WatchedMovie(Handler):
    """ Handles requests coming in to '/watched-it'
        e.g. www.flicklist.com/watched-it
    """

    def renderError(self, error_code):
        self.error(error_code)
        self.response.write("Oops! Something went wrong.")


    def post(self):
        watched_movie_id = self.request.get("watched-movie")

        watched_movie = Movie.get_by_id( int(watched_movie_id) )

        # if we can't find the movie, reject.
        if not watched_movie:
            self.renderError(400)
            return

        # update the movie's ".watched" property to True
        watched_movie.watched = True
        watched_movie.put()

        # render confirmation page
        t = jinja_env.get_template("watched-it-confirmation.html")
        content = t.render(movie = watched_movie)
        self.response.write(content)


class MovieRatings(Handler):

    def get(self):
        watched_movies = db.GqlQuery("SELECT * FROM Movie where watched = True order by created desc")
        t = jinja_env.get_template("ratings.html")
        content = t.render(movies = watched_movies)
        self.response.write(content)

    def post(self):
        rating = self.request.get("rating")
        movie_id = self.request.get("movie")

        movie = Movie.get_by_id( int(movie_id) )

        if movie and rating:
            movie.rating = rating
            movie.put()

            # render confirmation
            t = jinja_env.get_template("rating-confirmation.html")
            content = t.render(movie = movie)
            self.response.write(content)
        else:
            self.renderError(400)


class Login(Handler):

    def login_login_form(self, error=""):
        t = jinja_env.get_template("login.html")
        content = t.render(error=error)
        self.response.write(content)

    def get(self):
        self.render_login_form()

    def post(self):
        submitted_username = self.request.get('Username')
        submitted_password = self.request.get('password')

        user = self.get_user_by_name(submitted_username)
        if not user:
            self.render_login_form(error="Invalid")

            # TO DO: fix this stuff...needs to be finished


class Logout(Handler):

    def get(self):
        self.logout_user()
        self.redirect('/logout')


class Register(Handler):

    def validate_username(self, username):
        USER_RE = re.compile(r"^.{3,20}$")
        if USER_RE.match(username):
            return username
        return ""

    def validate_password(self, password):
        PWD_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        if USER_RE.match(password):
            return password
        return ""

    def validate_verify(self, password, verify):
        if password == verify:
            return verify


    def get(self):
        t = jinja_env.get_template('register.html')
        content = t.render(errors={})
        self.response.write(content)

    def post(self):
        submitted_username = self.request.get('username')
        submitted_password = self.request.get('password')
        submitted_verify = self.request.get('verify')

        username = self.validate_username(submitted_username)
        password = self.validate_username(submitted_password)
        verify = self.validate_username(submitted_password, submitted_verify)

        error = {}
        has_error = False

# TO Do: add item to prevent duplicate users


        if (username and password and verify):
            pw_hash = hashutils.make_pw_hash(username, password)
            user = User(username=username, pw_hash=pw_hash)
            user.put()

            self.login_user(user)

        else:
            has_error = True

            if not username:
                errors['username'] = 'Thats not a valid username'

            if not password:
                errors['password'] = 'Thats not a valid password'

            if not verify:
                errors['verify'] = 'Passwords do not match'

        if has_error:
            t = jinja_env.get_template('register.html')
            content = t.render(username=username, errors=errors)
            self.response.out.write(content)
        else:
            self.redirect('/')


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/add', AddMovie),
    ('/watched-it', WatchedMovie),
    ('/ratings', MovieRatings),
    ('/login', Login),
    ('/logout', Logout),
    ('/register', Register)
], debug=True)
