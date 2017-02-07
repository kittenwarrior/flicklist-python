import webapp2
import cgi
import jinja2
import os

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


def getUnwatchedMovies():
    """ Returns the list of movies the user wants to watch (but hasnt yet) """

    # for now, we are just pretending
    return [ "Star Wars", "Minions", "Freaky Friday", "My Favorite Martian" ]


def getWatchedMovies():
    """ Returns the list of movies the user has already watched """

    return [ "The Matrix", "The Dawg" ]


class Index(webapp2.RequestHandler):
    """ Handles requests coming in to '/' (the root of our site)
        e.g. www.flicklist.com/
    """

    def get(self):
        t = jinja_env.get_template("frontpage.html")
        content = t.render(
                        movies = getUnwatchedMovies(),
                        error = self.request.get("error"))
        self.response.write(content)

class AddMovie(webapp2.RequestHandler):
    """ Handles requests coming in to '/add'
        e.g. www.flicklist.com/add
    """

    def post(self):
        new_movie = self.request.get("new-movie")

        # if the user typed nothing at all, redirect and yell at them
        if (not new_movie) or (new_movie.strip() == ""):
            error = "Please specify the movie you want to add."
            self.redirect("/?error=" + cgi.escape(error))

        # if the user wants to add a terrible movie, redirect and yell at them
        if new_movie in terrible_movies:
            error = "Trust me, you don't want to add '{0}' to your Watchlist.".format(new_movie)
            self.redirect("/?error=" + cgi.escape(error, quote=True))

        # 'escape' the user's input so that if they typed HTML, it doesn't mess up our site
        new_movie_escaped = cgi.escape(new_movie, quote=True)

        # render the confirmation message
        t = jinja_env.get_template("add-confirmation.html")
        content = t.render(movie = new_movie_escaped)
        self.response.write(content)


class WatchedMovie(webapp2.RequestHandler):
    """ Handles requests coming in to '/watched-it'
        e.g. www.flicklist.com/watched-it
    """

    def renderError(self, error_code):
        self.error(error_code)
        self.response.write("Oops! Something went wrong.")


    def post(self):
        watched_movie = self.request.get("watched-movie")

        # if the movie movie is just whitespace (or nonexistant), reject.
        # (we didn't check for this last time--only checked in the AddMovie handler--but we probably should have!)
        if not watched_movie or watched_movie.strip() == "":
            self.renderError(400)
            return

        # if user tried to cross off a movie that is not in their list, reject
        if not (watched_movie in getUnwatchedMovies()):
            self.renderError(400)
            return

        # render confirmation page
        t = jinja_env.get_template("watched-it-confirmation.html")
        content = t.render(movie = watched_movie)
        self.response.write(content)


class MovieRatings(webapp2.RequestHandler):

    def get(self):
        t = jinja_env.get_template("ratings.html")
        content = t.render(movies = getWatchedMovies())
        self.response.write(content)


    def post(self):
        movie = self.request.get("movie")
        rating = self.request.get("rating")
        if movie and rating:
            t = jinja_env.get_template("rating-confirmation.html")
            content = t.render(movie=movie, rating=rating)
            self.response.write(content)
        else:
            self.renderError(400)




app = webapp2.WSGIApplication([
    ('/', Index),
    ('/add', AddMovie),
    ('/watched-it', WatchedMovie),
    ('/ratings', MovieRatings)
], debug=True)
