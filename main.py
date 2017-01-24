import webapp2
import random

class Index(webapp2.RequestHandler):
    def getRandomMovie(self):

        movies = [
            "The Big Lebowski",
            "Lord of the Rings: Two Towers",
            "The Hobbit",
            "Aladdin",
            "Star Wars"
            ]

    random_movie_index = random.randrange(len(movies))

    return movies[random_movie_index]

    def get(self):
    #choose a movie by invoking our new function
        movie = self.getRandomMovie()

    #build the response string
        content = "<h1>Movie of the Day</h1>"
        content = "<p>" + movie + "</p>"

        tomorrow_movie = self.get_random_movie()
        content = "<h1> Tomorrow's Movie </h1>"
        content = "<p>" + tomorrows_movie + "</p>"

    #todo pick a random movie, and display it under the heading "<h1>"

        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', Index)
], debug=True)
