import webapp2


# html boilerplate for the top of every page
page_header = """
<!DOCTYPE html>
<html>
<head>
    <title>FlickList</title>
</head>
<body>
    <h1>FlickList</h1>
"""

# html boilerplate for the bottom of every page
page_footer = """
</body>
</html>
"""


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

        cross_form = """
        <form action="/cross" method="post">
            <label>
                I want to cross off
                <select name="crossed-off-movie">
                    <option value="Star Wars">Star Wars</option>
                    <option value="Minions">Minions</option>
                    <option value="The Hobbit">The Hobbit</option>
                    <option vlaue="John Wick">John Wick</option>
                </select>
            </label>
            <input type="submit" value="Cross It Off"/>
        </form>
        """


        content = page_header + edit_header + add_form + cross_form + page_footer
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
    """ Handles requests coming in to '/cross'
        e.g. www.flicklist.com/cross
    """

    def post(self):
        # look inside the request to figure out what the user typed
        crossoff_movie = self.request.get("crossed-off-movie")

        # build response content
        crossoff_movie_element = "<strike>" + crossoff_movie + "</strike>"
        sentence = crossoff_movie_element + " has been crossed off to your Watchlist!"

        content = page_header + "<p>" + sentence + "</p>" + page_footer
        self.response.write(content)


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/add', AddMovie),
    ('/cross', CrossOffMovie)
], debug=True)
