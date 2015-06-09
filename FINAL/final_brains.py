
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
    if self.state is "curious":
      if message == 'timer':
        # go to a random point, wake up sometime in the next 10 seconds
        world = self.body.world
        x, y = random.random()*world.width, random.random()*world.height
        self.body.go_to((x,y))
        self.body.set_alarm(random.random()*10)
      elif message == 'collide' and details['what'] == 'Player':
        # a slug bumped into us; get curious
        self.state = "attack"
        #self.body.set_alarm(1) # think about this for a sec
        self.target = details['who']

    elif self.state is "attack":
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
      if details == 'a':
        self.state = 'attack'
      elif details == 'i':
        self.state = 'idle'
      elif details == 'h':
        self.state = 'harvest'
      elif details == 'b':
        self.state = 'build'
      elif details == 'q':
        self.state = 'idle'
        self.body.amount -= .10
      elif details == 'w':
        if self.body.amount > 1.0:
          self.body.amount = 1.0  
        self.body.amount += .10
        self.state = 'idle'

    if message == 'collide' and details['what'] == 'Medkit':
      medkit = details['who']
      medkit.destroy()
      self.body.amount = 1.0

    if self.state == 'idle':
      self.body.stop()
    elif self.state == 'attack':
      if message == 'timer':
        try:
          zombie = self.body.find_nearest('Zombie')
          self.body.follow(zombie)
        except:
          self.state = 'idle'
          print "No more zombies"
      elif message == 'collide' and details['what'] == 'Zombie':
        zombie = details['who']
        zombie.amount -= 0.05
    elif self.state == 'build':
      nest = self.body.find_nearest('Nest')
      if message == 'timer':
        nest = self.body.find_nearest('Nest')
        self.body.go_to(nest)
      elif message == 'collide' and details['what'] == 'Nest':
        nest = details['who']
        nest.amount += 0.05
      elif nest.amount >= 1:
        self.state = 'idle'
    elif self.state == 'harvest':
      if self.has_resource == True:
        nest = self.body.find_nearest('Nest')
        if message == 'timer':
          nest = self.body.find_nearest('Nest')
          self.body.go_to(nest)
        elif message == 'collide' and details['what'] == 'Nest':
          self.has_resource = False
      elif self.has_resource == False:
        try:
          resource = self.body.find_nearest('Resource')
          if message == 'timer':
            resource = self.body.find_nearest('Resource')
            self.body.go_to(resource)
          elif message == 'collide' and details['what'] == 'Resource':
            self.has_resource = True
            resource = details['who']
            resource.amount -= 0.25
        except:
          self.state = 'idle'
          print "No more resources."
    self.body.set_alarm(1)



world_specification = {
  #'worldgen_seed': 13, # comment-out to randomize
  'nests': 0,
  'obstacles': 0,
  'resources': 0,
  'players': 1,
  'zombies': 0,
  'medkit': 0,
}

brain_classes = {
  'zombie': ZombieBrain,
  'player': PlayerBrain,
}
