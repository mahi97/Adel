class Vec2D:
  def __init__(self):
    self.x = 0
    self.y = 0


class Object:
  def __init__(self, id):
    self.pos = Vec2D()
    self.vel = Vec2D()
    self.acc = Vec2D()
    self.dir = 0
    self.id = id


class WorldModel:
  def __init__(self):
    self.ball = Object(-1)
    self.robotA = [Object(i) for i in range(5)]
    self.robotB = [Object(i) for i in range(5)]

  def update(self, frame):
    pass
