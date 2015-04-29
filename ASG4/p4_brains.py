
import random

# EXAMPLE STATE MACHINE
class MantisBrain:

  def __init__(self, body):
    self.body = body
    self.state = 'idle'
    self.target = None

  def handle_event(self, message, details):

    if self.state is 'idle':

      if message == 'timer':
        # go to a random point, wake up sometime in the next 10 seconds
        world = self.body.world
        x, y = random.random()*world.width, random.random()*world.height
        self.body.go_to((x,y))
        self.body.set_alarm(random.random()*10)

      elif message == 'collide' and details['what'] == 'Slug':
        # a slug bumped into us; get curious
        self.state = 'curious'
        self.body.set_alarm(1) # think about this for a sec
        self.body.stop()
        self.target = details['who']

    elif self.state == 'curious':

      if message == 'timer':
        # chase down that slug who bumped into us
        if self.target:
          if random.random() < 0.5:
            self.body.stop()
            self.state = 'idle'
          else:
            self.body.follow(self.target)
          self.body.set_alarm(1)
      elif message == 'collide' and details['what'] == 'Slug':
        # we meet again!
        slug = details['who']
        slug.amount -= 0.01 # take a tiny little bite
    
class SlugBrain:

  def __init__(self, body):
    self.body = body
    self.state = 'idle'
    self.target = None
    self.has_resource = False


  def handle_event(self, message, details):
    # TODO: IMPLEMENT THIS METHOD
    #  (Use helper methods and classes to keep your code organized where
    #  approprioate.)
    if self.body.amount < 0.5:
      self.state = 'flee'

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

    if self.state == 'idle':
      self.body.stop()
    elif self.state == 'attack':
      if message == 'timer':
        try:
          mantis = self.body.find_nearest('Mantis')
          self.body.follow(mantis)
        except:
          self.state = 'idle'
          print "No more mantises"
      elif message == 'collide' and details['what'] == 'Mantis':
        mantis = details['who']
        mantis.amount -= 0.05
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
    elif self.state == 'flee':
      nest = self.body.find_nearest('Nest')
      self.body.go_to(nest)
      if message == 'collide' and details['what'] == 'Nest':
        self.body.amount += 0.01
      elif self.body.amount >= 1:
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
  'worldgen_seed': 13, # comment-out to randomize
  'nests': 2,
  'obstacles': 25,
  'resources': 2,
  'slugs': 5,
  'mantises': 5,
}

brain_classes = {
  'mantis': MantisBrain,
  'slug': SlugBrain,
}
