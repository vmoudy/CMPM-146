
import random

# EXAMPLE STATE MACHINE
class ZombieBrain:

  def __init__(self, body):
    self.body = body
    self.state = self.body.world.zombie_state
    self.target = None    

  def handle_event(self, message, details):
    self.state = self.body.world.zombie_state

    if not self.body.world.player_alive:
      self.state = "curious"

    if self.state == "curious":
      if message == 'timer':
        # go to a random point, wake up sometime in the next 10 seconds
        world = self.body.world
        x, y = random.random()*world.width, random.random()*world.height
        self.body.go_to((x,y))
        self.body.set_alarm(1)
      elif message == 'collide' and details['what'] == 'Player':
        # a slug bumped into us; get curious
        self.state = "attack"
        self.body.set_alarm(1) # think about this for a sec
        self.target = details['who']

    elif self.state == "attack":
      self.body.follow(self.body.world.player)
      self.body.set_alarm(1)
      if message == 'collide' and details['what'] == 'Player':
        # we meet again!
        player = details['who']
        player.amount -= 0.01 # take a tiny little bite
    
class PlayerBrain:

  def __init__(self, body):
    self.body = body
    self.state = 'idle'
    self.target = None
    self.has_resource = False

  def handle_event(self, message, details):
    # TODO: IMPLEMENT THIS METHOD
    #  (Use helper methods and classes to keep your code organized where
    #  approprioate.)

    if message == 'order' and isinstance(details, tuple):
      self.state = 'moving'
      x, y = details
      self.body.go_to((x, y))
    elif message == 'order' and isinstance(details, basestring):
      if details == 'p':
        self.body.amount -= .10
      elif details == 'o':
        if self.body.amount > 1.0:
          self.body.amount = 1.0  
        self.body.amount += .10
      elif details == 'd':
        x, y = self.body.position
        x += 5
        self.body.position = (x, y)
      elif details == 'a':
        x, y = self.body.position
        x -= 5
        self.body.position = (x, y)
      elif details == 'w':
        x, y = self.body.position
        y -= 5
        self.body.position = (x, y)
      elif details == 's':
        x, y = self.body.position
        y += 5
        self.body.position = (x, y)

    if message == 'collide' and details['what'] == 'Medkit':
      medkit = details['who']
      medkit.destroy()
      self.body.amount = 1.0

    if message == 'collide' and details['what'] == 'Ammo':
      ammo = details['who']
      ammo.destroy()
      self.body.world.ammo.set(31)

    if message == 'collide' and details['what'] == 'Zombie':
      zombie = details['who']
      zombie.state = "attack"
      
    self.body.set_alarm(1)



world_specification = {
  #'worldgen_seed': 13, # comment-out to randomize
  'nests': 0,
  'obstacles': 0,
  'resources': 0,
  'players': 1,
  'zombies': 0,
  'medkit': 0,
  'ammo': 0,
}

brain_classes = {
  'zombie': ZombieBrain,
  'player': PlayerBrain,
}
