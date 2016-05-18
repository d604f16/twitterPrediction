class Tweet:
  'Simple representation of a tweet'
  def __init__(self, id, user, txt, location):
    self.id = id
    self.user = user
    self.txt = txt
    self.location = location

  def __str__(self):
    return "[" + self.id + ", " + self.user + ", " + self.txt + ", " + self.location + "]"
