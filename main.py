import webapp2

classHelloWorld(webapp2.RequestHandler):
  defget(self):
    self.response.write('Hello from App Engine!');

app = webapp2.WSGIApplication([
  ('/', HelloWorld),
])
