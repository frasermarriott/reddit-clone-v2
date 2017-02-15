from flask import session, request
import unittest
import app

class frontpageTest(unittest.TestCase):
  def test_root(self):
    self.app = app.app.test_client()
    out = self.app.get('/')
    assert '200 OK' in out.status
    assert 'charset=utf-8' in out.content_type
    assert 'text/html' in out.content_type


#: test if user is redirected when attempting to access certain pages when already logged in
class testSession(unittest.TestCase):
  def test_session(self):
    self.app = app.app.test_client()

    with self.app.session_transaction() as sess:
      #: set a fake session to test
      sess['user_id'] = 'testID'

    out = self.app.get('/register')
    out = self.app.get('/register/new')
    #out = self.app.get('/login')
    assert '302' in out.status
    assert 'charset=utf-8' in out.content_type
    assert 'text/html' in out.content_type


class testLogin(unittest.TestCase):

  def test_login(self):
    self.app = app.app.test_client()
    out = self.app.post('/login', data=dict(username='fraser',password='fraser'), follow_redirects=True)
    assert '200 OK' in out.status
    assert 'charset=utf-8' in out.content_type
    assert 'text/html' in out.content_type

  def test_incorrect_login(self):
    self.app = app.app.test_client()
    out = self.app.post('/login', data=dict(username='fraser',password='wrong'), follow_redirects=True)
    assert '401' in out.status
    assert 'text/html' in out.content_type



if __name__ == "__main__":
  unittest.main()
