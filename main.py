import webapp2
import cgi


# html boilerplate for the top of every page
page_header = """
<!DOCTYPE html>
<html>
<head>
    <title>FlickList</title>
    <style type="test/css">
        .error {
            color: red;
        }
    </style>
</head>
<body>
    <h1>FlickList</h1>
"""

# html boilerplate for the bottom of every page
page_footer = """
</body>
</html>
"""


def getCurrentWatchList():
    '''returns the user's current watch list '''
    return ("Star Wars", "Minions", "Freaky Friday", "My Favorite Martian")


class Index(webapp2.RequestHandler):
    """ Handles requests coming in to '/' (the root of our site)
        e.g. www.flicklist.com/
    """

    def get(self):

        edit_header = "<h3>Edit My Watchlist</h3>"

        # a form for adding new movies
        add_form = """
        <form action="/add" method="post">
            <label>
                I want to add
                <input type="text" name="new-movie"/>
                to my watchlist.
            </label>
            <input type="submit" value="Add It"/>
        </form>
        """

        #create the <options> for our cross off <select>
        crossoff_options = ""
        for movie in getCurrentWatchList():
            crossoff_options += "<option value='{0}'>{0}</options>".format(movie)

        # a form for crossing off movies
        crossoff_form = """
        <form action="/cross-off" method="post">
            <label>
                I want to cross off
                <select name="crossed-off-movie"/>
                    {0}
                </select>
                from my watchlist.
            </label>
            <input type="submit" value="Cross It Off"/>
        </form>
        """.format(crossoff_options)

        error= self.request.get("error")
        if error:
            error_element = "<p class='error'>" + cgi.escape(error, quote=True) + "</p>"
        else:
            error_element = ""

        main_content = edit_header + add_form + crossoff_form + error_element
        page_content = edit_header + add_form + crossoff_form
        content = page_header + main_content + page_footer
        self.response.write(content)


class AddMovie(webapp2.RequestHandler):
    """ Handles requests coming in to '/add'
        e.g. www.flicklist.com/add
    """

    def post(self):
        # look inside the request to figure out what the user typed
        new_movie = self.request.get("new-movie")

        # build response content
        new_movie_element = "<strong>" + new_movie + "</strong>"
        sentence = new_movie_element + " has been added to your Watchlist!"

        content = page_header + "<p>" + sentence + "</p>" + page_footer
        self.response.write(content)



class CrossOffMovie(webapp2.RequestHandler):
    """ Handles requests coming in to '/cross-off'
        e.g. www.flicklist.com/cross-off
    """

    def post(self):
        # look inside the request to figure out what the user typed
        crossed_off_movie = self.request.get("crossed-off-movie")

        if crossed_off_movie not in getCurrentWatchList():
            #start building error message
            error = "'{0}' is not in your watchlist, so you can't cross it off".format(crossed_off_movie)
            error_escaped_message = cgi.escape(error, quote=True)

            self.redirect("/?error=" + error_escaped_message)

        # build response content
        #Everything looks good keep on going forward
        crossed_off_movie_element = "<strike>" + crossed_off_movie + "</strike>"
        confirmation = crossed_off_movie_element + " has been crossed off your Watchlist."

        content = page_header + "<p>" + confirmation + "</p>" + page_footer
        self.response.write(content)


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/add', AddMovie),
    ('/cross-off', CrossOffMovie)
], debug=True)
