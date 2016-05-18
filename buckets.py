class Buckets:
  'Used for bucketezing data'
  
  def __init__(self, count):
    self.buckets = []
    for x in range(0, count):
      self.buckets.append([])

  def add(self, object):
    min(self.buckets,key=len).append(object)
