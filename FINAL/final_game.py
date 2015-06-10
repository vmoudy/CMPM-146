import final_brains
import Tkinter
import collections
import random
import sys
import math
import heapq

class MicroDirector:
  """container for many GameObject instances and some global parameters"""

  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.all_objects = []
    self.player = []
    self.zombies = []
    self.objects_by_class = collections.defaultdict(list)
    self.sel_a = None
    self.sel_b = None
    self.selection = {}
    self.time = 0
    self.ai_on_off = Tkinter.IntVar()
    self.change_text = Tkinter.StringVar()
    b = Tkinter.Button(master, textvariable=self.change_text, command=self.callback)
    b.grid(row=1, column=0)
    self.change_text.set("Micro-Director is on")
    self.ai_on_off.set(1)
    self.spawn_ammo = False
    self.spawn_health = False
    self.max_health = 1
    self.health_amount = 0
    self.max_ammo = 1
    self.ammo_amount = 0
    self.current_state = Tkinter.StringVar()
    self.current_state.set("calm")
    self.zombie_amount = Tkinter.IntVar()
    self.zombie_amount.set(0)
    self.zombie_state = "curious"
    self.max_zombies = 45
    self.player_alive = True
    self.ammo = Tkinter.IntVar()
    self.ammo.set(31)
    self.accuracy = 0
    self.hit = 0
    self.shots = 0
    self.multiplier = 0
    print "Intensity: Calm"

  def callback(self):
    if not self.ai_on_off.get():
      self.change_text.set("Micro-Director is on")
      self.ai_on_off.set(1)
      #print self.ai_on_off.get()
    else:
      self.change_text.set("Micro-Director is off")
      self.ai_on_off.set(0)
      #print self.ai_on_off.get()

  def bbox(self, obj):
    x, y = obj.position
    if x <= self.width/2:
      if y <= self.height/2:
        return "q1"
      else:
        return "q3"
    elif x > self.width/2:
      if y <= self.height/2:
        return "q2"
      else:
        return "q4"

  def register(self, obj):
    """add a GameObject to the all_objects and objects_by_class lists"""
    assert isinstance(obj, GameObject)

    if obj not in self.all_objects:
      self.all_objects.append(obj)

    clazz = obj.__class__
    if obj not in self.objects_by_class[clazz]:
      self.objects_by_class[clazz].append(obj)
 
  def unregister(self, obj):
    """remove a GameObject from the all_objects and objects_by_class lists"""
    assert isinstance(obj, GameObject)
    if obj in self.all_objects:
      self.all_objects.remove(obj)

    clazz = obj.__class__
    if obj in self.objects_by_class[clazz]:
      self.objects_by_class[clazz].remove(obj)

    if obj in self.selection:
      del self.selection[obj]

  def draw(self,canvas):
    """draw the whole game world to the canvas"""

    canvas.delete(Tkinter.ALL)

    # backdrop
    """canvas.create_rectangle(0, 0, self.width, self.height, fill='grey', outline='')
    s = Tkinter.Label(master, text="Intensity")
    s.grid(row=1, column=0)
    t = Tkinter.Label(master, textvariable=self.current_state)
    t.grid(row=2, column=0)
    h = Tkinter.Label(master, text="Zombie amount")
    h.grid(row=1, column=1)
    z = Tkinter.Label(master, textvariable=self.zombie_amount)
    z.grid(row=2, column=1)
    at = Tkinter.Label(master, text="Ammo count")
    at.grid(row=1, column=2)
    a = Tkinter.Label(master, textvariable=self.ammo)
    a.grid(row=2, column=2)"""

    # child objects
    for obj in self.all_objects:
      obj.draw(canvas)

    # highlight selected objects
    if self.selection:
      for c in self.selection:
        canvas.create_rectangle(
            c.position[0]-c.radius-1,
            c.position[1]-c.radius-1,
            c.position[0]+c.radius+1,
            c.position[1]+c.radius+1,
            outline='green',
            fill='',
            width=2.0)

    # draw the user's partial selection box 
    if self.sel_a and self.sel_b:
      top_left = (min(self.sel_a[0], self.sel_b[0]), min(self.sel_a[1], self.sel_b[1]))
      bottom_right = (max(self.sel_a[0], self.sel_b[0]), max(self.sel_a[1], self.sel_b[1]))
      canvas.create_rectangle(
          top_left[0],
          top_left[1],
          bottom_right[0],
          bottom_right[1],
          outline='green',
          fill='',
          width=2.0)

  def build_distance_field(self, target, blockers=[], expansion=0):
    """build a low-resolution distance map and return a function that uses
    bilinear interpolation to look up continuous positions"""

    bin_size = 20

    obstacles = {} # (i,j) -> bool 

    # paint no-obstacles over the map
    for i in range(self.width/bin_size):
      for j in range(self.height/bin_size):
        obstacles[(i,j)] = False

    # rasterize collision space of each object
    for obj in blockers:
      i_lo = int((obj.position[0] - obj.radius)/bin_size - 1)
      i_hi = int((obj.position[0] + obj.radius)/bin_size + 1)
      j_lo = int((obj.position[1] - obj.radius)/bin_size - 1)
      j_hi = int((obj.position[1] + obj.radius)/bin_size + 1)
      for i in range(i_lo, i_hi+1):
        for j in range(j_lo, j_hi+1):
          x, y = i*bin_size, j*bin_size
          dx = obj.position[0]-x
          dy = obj.position[1]-y
          dist = math.sqrt(dx*dx+dy*dy)
          if dist < obj.radius + expansion:
            obstacles[(i,j)] = True

    # dijkstra's algorithm to build distance map
    dist = {}
    start = (int(target[0]/bin_size), int(target[1]/bin_size))
    dist[start] = 0
    queue = [(0,start)]
    while queue:
      d, c = heapq.heappop(queue)
      for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
        next_c = (c[0] + di, c[1] + dj)
        if next_c in obstacles:

          if not obstacles[next_c]:
            cost = 1
          else:
            cost = 1e6
          next_d = d + cost
          if next_c not in dist or next_d < dist[next_c]:
            dist[next_c] = d
            heapq.heappush(queue, (next_d, next_c))

    def lookup(position): # bilinear interpolation
      x,y = position
      alpha = float(x % bin_size)/bin_size
      beta = float(y % bin_size)/bin_size
      i, j = int(x / bin_size), int(y / bin_size)
      dx = x - self.width/2
      dy = y - self.height/2
      default = 2*math.sqrt(dx*dx+dy*dy)
      a = dist.get((i,j),default)
      b = dist.get((i+1,j),default)
      c = dist.get((i,j+1),default)
      d = dist.get((i+1,j+1),default)
      ab = (1-alpha)*a + alpha*b
      cd = (1-alpha)*c + alpha*d
      abcd = (1-beta)*ab + beta*cd
      return abcd

    return lookup

  def update(self, dt):
    """update the world and all registered GameObject instances"""

    def give_health():
      if self.ai_on_off.get():
        if self.health_amount <= self.max_health and self.multiplier == 2:
          where = self.bbox(self.player)
          self.multiplier = 1
          if where == "q1":
            return (780, 580)
          elif where == "q2":
            return (20, 20)
          elif where == "q3":
            return (780, 20)
          else: #where == "q4"
            return (20, 580)
        elif self.health_amount <= self.max_health:
          where = self.bbox(self.player)
          if where == "q1":
            return (20, 20)
          elif where == "q2":
            return (780, 20)
          elif where == "q3":
            return (20, 580)
          else: #where == "q4"
            return (780, 580)
      else:
        return (random.random()*self.width, random.random()*self.height)

    def give_ammo():
      if self.ai_on_off.get():
        if self.ammo_amount <= self.max_ammo and self.accuracy <= 0.5 and self.multiplier == 2:
          where = self.bbox(self.player)
          self.multiplier = 1
          if where == "q1":
            return (765, 35)
          elif where == "q2":
            return (35, 595)
          elif where == "q3":
            return (765, 565) 
          else: #where == "q4"
            return (45, 45)    
        elif self.ammo_amount <= self.max_ammo:
          where = self.bbox(self.player)
          if where == "q1":
            return (45, 45)
          elif where == "q2":
            return (765, 35)
          elif where == "q3":
            return (35, 595)
          else: #where == "q4"
            return (765, 565)
      else:
        return (random.random()*self.width, random.random()*self.height)

    self.check_state()
    self.spawn_zombies()
    self.check_health()
    self.check_ammo()

    if self.ai_on_off.get():
      if (self.current_state.get() == "calm" or self.current_state.get() == "relaxing"):
        self.multiplier = 1
      elif (self.current_state.get() == "insane" or self.current_state.get() == "rising"):
        self.multiplier = 2
      #print self.spawn_health and self.health_amount < self.max_health
      if self.spawn_health and self.health_amount < self.max_health:
        i = 0
        while i <= self.multiplier:
          h = Medkit(self)
          h.position = give_health()
          self.register(h)
          self.health_amount += 1
          i = i + 1
        self.spawn_health = False
      if self.spawn_ammo and self.ammo_amount < self.max_ammo:
        i = 0
        while i <= self.multiplier:
          a = Ammo(self)
          a.position = give_ammo()
          self.register(a)
          self.ammo_amount += 1
          i = i + 1
        self.spawn_ammo = False
    else:
      if self.spawn_health and self.health_amount < 5:
        h = Medkit(self)
        h.position = give_health()
        self.register(h)
        self.health_amount += 1
      if self.spawn_ammo and self.ammo_amount < 5:
        a = Ammo(self)
        a.position = give_ammo()
        self.register(a)
        self.ammo_amount += 1
    self.time += dt

    # update all objects
    for obj in self.all_objects:
      obj.update(dt)

    # let brains handle collision reactions
    def handle_collision(a,b):
      if a.brain: a.brain.handle_event('collide',{'what': str(b.__class__.__name__), 'who': b})
      if b.brain: b.brain.handle_event('collide',{'what': str(a.__class__.__name__), 'who': a})

    # collide within species
    for animal in [Player,Zombie]:
      self.eject_colliders(self.objects_by_class[animal],self.objects_by_class[animal],randomize=True)

    # collide across species
    self.eject_colliders(self.objects_by_class[Zombie],self.objects_by_class[Player],randomize=True,handler=handle_collision)

    # collide animals with minerals without handlers
    for animal in [Player,Zombie]:
      for mineral in [Obstacle]:
        self.eject_colliders(self.objects_by_class[animal],self.objects_by_class[mineral])

    # collide animals with minerals with handlers
    for animal in [Player,Zombie]:
      for mineral in [Nest,Resource,Medkit,Ammo]:
        self.eject_colliders(self.objects_by_class[animal],self.objects_by_class[mineral],handler=handle_collision)

    # clean up objects with negative amount values
    for obj in self.all_objects:
      if obj.amount < 0:
        obj.destroy()
      elif obj.amount > 1:
        obj.amount = 1.0

  def check_health(self):
    if self.player.amount < .30:
      self.spawn_health = True

  def check_ammo(self):
    if self.ammo.get() <= 5:
      self.spawn_ammo = True

  def eject_colliders(self, firsts, seconds, randomize=False, handler=None):
    
    def eject(o1, o2):
      if o1 != o2:
        dx = o1.position[0] - o2.position[0]
        dy = o1.position[1] - o2.position[1]
        dist = math.sqrt(dx*dx+dy*dy) + 0.001
        if dist < o1.radius + o2.radius:
          extra = dist - (o1.radius + o2.radius)
          fraction = extra / dist
          if handler: handler(o1,o2) # let colliders know they collided!
          if randomize and random.random() < 0.5:
            o2.position = (o2.position[0] + fraction*dx, o2.position[1] + fraction*dy)
          else:
            o1.position = (o1.position[0] - fraction*dx, o1.position[1] - fraction*dy)

    def sorted_with_bounds(objects):
      return sorted([(o.position[0]-o.radius, 'add', o) for o in objects] +
                    [(o.position[0]+o.radius, 'remove', o) for o in objects])

    active_firsts = {}
    active_seconds = {}

    firsts_with_bounds = sorted_with_bounds(firsts)
    seconds_with_bounds = sorted_with_bounds(seconds)

    while firsts_with_bounds and seconds_with_bounds:

      o1_key, o1_cmd, o1 = firsts_with_bounds[0]
      o2_key, o2_cmd, o2 = seconds_with_bounds[0]

      if o1_key < o2_key:
        firsts_with_bounds.pop(0)
        if o1_cmd is 'add':
          active_firsts[o1] = True
          for o2 in active_seconds:
            eject(o1,o2)
        else:
          del active_firsts[o1]
      else:
        seconds_with_bounds.pop(0)
        if o2_cmd is 'add':
          active_seconds[o2] = True
          for o1 in active_firsts:
            eject(o1,o2)
        else:
          del active_seconds[o2]

  def populate(self, specification, brain_classes):
    """create an interesting randomized level design"""

    if 'worldgen_seed' in specification:
      random.seed(specification['worldgen_seed'])

    def random_position():
      return (random.random()*self.width, random.random()*self.height)

    for i in range(specification.get('nests',0)):
      n = Nest(self)
      n.position = random_position()
      self.register(n)

    for i in range(specification.get('obstacles',0)):
      o = Obstacle(self)
      o.radius = 5+250*random.random()*random.random()*random.random()
      o.position = random_position()
      self.register(o)

    for i in range(specification.get('resources',0)):
      r = Resource(self)
      r.position = random_position()
      r.amount = random.random()
      self.register(r)

    for i in range(specification.get('medkit',0)):
      m = Medkit(self)
      m.position = random_position()
      self.register(m)

    for i in range(specification.get('ammo',0)):
      a = Ammo(self)
      a.position = random_position()
      self.register(a)

    for i in range(specification.get('players',0)):
      p = Player(self)
      p.position = (200, 150)
      p.brain = brain_classes['player'](p)
      p.set_alarm(0)
      self.register(p)
      self.player = p

    for i in range(specification.get('zombies',0)):
      z = Zombie(self)
      z.position = random_position()
      z.brain = brain_classes['zombie'](z)
      z.set_alarm(0)
      self.register(z)

    for i in range(10): # jiggle the world around for a while so it looks pretty
      self.eject_colliders(self.all_objects,self.all_objects,randomize=True)

  def find_nearest(self, searcher, clazz=None, where=None):
    """find the nearest object of the given class and property according to
    navigable distance"""

    field = self.build_distance_field(
        searcher.position,
        self.all_objects,
        -searcher.radius)

    if clazz:
      candidates = self.objects_by_class[clazz]
    else:
      candidates = self.all_objects

    return min(filter(where,candidates),key=lambda obj: field(obj.position))

  def issue_selection_order(self, order):
    """apply user's order (a key or right-click location) to the selected
    objects"""

    for obj in self.all_objects:
      if obj.name == 'Player':
        if obj.brain:
          obj.brain.handle_event('order',order)

  def shoot(self):
    self.shots = self.shots + 1.0
    for obj in self.all_objects:
      if obj.name == 'Zombie':
        xdiff = abs(obj.position[0] - self.sel_b[0])
        ydiff = abs(obj.position[1] - self.sel_b[1])
        if (math.sqrt((math.pow(xdiff, 2)) + (math.pow(ydiff, 2)))) <= 10:
          obj.destroy()
          self.hit = self.hit + 1.0
    self.accuracy = self.hit/self.shots
    print "Accuracy: ", self.accuracy
    if self.ammo.get() == 0:
      print "Out of ammo!"

  def make_selection(self):
    """build selection from the set of units contained in the sel_a-to-sel_b
    bounding box"""

    top_left = (min(self.sel_a[0], self.sel_b[0]), min(self.sel_a[1], self.sel_b[1]))
    bottom_right = (max(self.sel_a[0], self.sel_b[0]), max(self.sel_a[1], self.sel_b[1]))
    self.selection = {}
    for obj in self.objects_by_class[Player]:
      if      top_left[0] < obj.position[0] \
          and top_left[1] < obj.position[1] \
          and obj.position[0] < bottom_right[0] \
          and obj.position[1] < bottom_right[1]:
            self.selection[obj] = True
    self.sel_a = None
    self.sel_b = None

  def clear_selection(self):
    self.selection = {}

  def spawn_zombies(self):

    def set_spawn_point(obj):
      if self.ai_on_off.get():
        where = self.bbox(obj)
        if where == "q1":
          return (780, 580)
        elif where == "q2":
          return (20, 580)
        elif where == "q3":
          return (780, 20)
        else: #where == "q4"
          return (20, 20)
      else:
        return (random.random()*self.width, random.random()*self.height)

    if (self.current_state.get() == "calm") and self.zombie_amount.get() < self.max_zombies:
      if (self.time - (5.0*self.zombie_amount.get()) >= 0):
        m = Zombie(self)
        m.position = set_spawn_point(self.player)
        m.brain = final_brains.brain_classes['zombie'](m)
        m.set_alarm(0)
        self.register(m)
        self.zombie_amount.set(self.zombie_amount.get() + 1)
    if (self.current_state.get() == "rising") and self.zombie_amount.get() < self.max_zombies:
      if (self.time - (2.0*self.zombie_amount.get()) >= 0):
        m = Zombie(self)
        m.position = set_spawn_point(self.player)
        m.brain = final_brains.brain_classes['zombie'](m)
        m.set_alarm(0)
        self.register(m)
        self.zombie_amount.set(self.zombie_amount.get() + 1)
    for i in range(10): # jiggle the world around for a while so it looks pretty
      self.eject_colliders(self.all_objects,self.all_objects,randomize=True)
    
  def check_state(self):
    if self.ai_on_off.get():
      if self.current_state.get() == "calm" and self.zombie_amount.get() >= 5:
        self.current_state.set("rising")
        self.zombie_state = "attack"
        print "Intensity: Rising"
      elif self.current_state.get() == "rising" and self.zombie_amount.get() == self.max_zombies:
        self.current_state.set("insane")
        print "Intensity: insane"
      elif self.current_state.get() == "insane" and self.zombie_amount.get() <= self.max_zombies/3:
        self.current_state.set("relaxing")
        print "Intensity: Relaxing"
      elif self.current_state.get() == "relaxing" and self.zombie_amount.get() == 0:
        print "Intensity: Calm"
        self.current_state.set("calm")
        self.zombie_state = "curious"
    else:
      self.current_state.set("calm")
      self.zombie_state = "curious"

class Controller(object):
  """base class for simulation-rate GameObject controllers"""
  def update(self, obj, dt):
    pass

class ObjectFollower(Controller):
  """behavior of following another object via direct approach"""

  def __init__(self, target):
    self.target = target

  def update(self, obj, dt):
    dx = self.target.position[0] - obj.position[0]
    dy = self.target.position[1] - obj.position[1]
    mag = math.sqrt(dx*dx+dy*dy)
    obj.position = (obj.position[0] + dt*obj.speed*dx/mag,
                    obj.position[1] + dt*obj.speed*dy/mag)

class FieldFollower(Controller):
  """behavior of descending a given distance field"""

  def __init__(self, field):
    self.field = field

  def update(self, obj, dt):
    x, y = obj.position
    eps = 0.1
    gx = self.field((x+eps,y)) - self.field((x-eps,y))
    gy = self.field((x,y+eps)) - self.field((x,y-eps))
    mag = math.sqrt(gx*gx+gy*gy)
    if mag:
      obj.position = (obj.position[0] - dt*obj.speed*gx/mag,
                      obj.position[1] - dt*obj.speed*gy/mag)

class GameObject(object):
  """base class for objects managed by a World"""

  def __init__(self, world):
    self.world = world
    self.radius = 10
    self.color = 'gray'
    self.position = None
    self.controller = None
    self.brain = None
    self.amount = 1.0 # a generic value that is visualized in the graphics
    self.timer_deadline = None

  def __repr__(self):
    return '<%s %d>' % (str(self.__class__.__name__), id(self))

  def draw(self, canvas):
    """draw a generic object to the screen using it's position, radius, color, and amount"""
    self.borders()
    if self.position:
      sa = math.sqrt(self.amount)
      canvas.create_oval(
          self.position[0]-self.radius*sa,
          self.position[1]-self.radius*sa,
          self.position[0]+self.radius*sa,
          self.position[1]+self.radius*sa,
          outline='',
          fill=self.color)
      canvas.create_oval(
          self.position[0]-self.radius,
          self.position[1]-self.radius,
          self.position[0]+self.radius,
          self.position[1]+self.radius,
          outline='black',
          fill='')

  def borders(self):
    x, y = self.position 
    world = self.world
    sa = math.sqrt(self.amount)
    if x < -self.radius*sa:
      x = world.width + self.radius*sa

    if y < -self.radius*sa:
      y = world.height + self.radius*sa

    if x > world.width + self.radius*sa:
      x = -self.radius*sa

    if y > world.height + self.radius*sa:
      y = -self.radius*sa

    self.position = (x, y)

  def get_amount(self):
    return self.amount

  def update(self, dt):
    """handle simulation-rate updates by delegating to controller"""
    if self.timer_deadline is not None:
      if self.timer_deadline < self.world.time:
        self.timer_deadline = None
        if self.brain:
          self.brain.handle_event('timer', None)

    if self.controller:
      self.controller.update(self, dt)

  def go_to(self, target):
    blockers = [obj for obj in self.world.all_objects if obj is not target and obj is not self]
    position = target.position if isinstance(target, GameObject) else target
    field = self.world.build_distance_field(position, blockers, self.radius)
    field_follower = FieldFollower(field)
    self.controller = field_follower

  def find_nearest(self, classname):
    clazz = eval(classname)
    return self.world.find_nearest(self, clazz)

  def follow(self, target):
    self.controller = ObjectFollower(target)

  def stop(self):
    self.controller = None

  def destroy(self):
    self.world.unregister(self)
    if self.name == "Zombie":
      self.world.zombie_amount.set(self.world.zombie_amount.get() - 1)
    if self.name == "Medkit":
      self.world.health_amount -= 1
    if self.name == "Player":
      self.world.player_alive = False
    if self.name == "Ammo":
      self.world.ammo_amount -= 1

  def set_alarm(self, dt):
    when = self.world.time + dt
    if self.timer_deadline is None or when < self.timer_deadline:
      self.timer_deadline = when

class Nest(GameObject):
  """home-base for Team Player"""
  def __init__(self, world):
    super(Nest, self).__init__(world)
    self.name = "Nest"
    self.radius = 100
    self.amount = 0.5
    self.color = 'orange'
  
class Obstacle(GameObject):
  """an impassable rocky obstacle"""
  def __init__(self, world):
    super(Obstacle, self).__init__(world)
    self.name = "Obstacle"
    self.radius = 25
    self.color = 'gray'

class Resource(GameObject):
  """a tasty clump of resources to be consumed"""
  def __init__(self, world):
    super(Resource, self).__init__(world)
    self.name = "Resource"
    self.radius = 25
    self.color = 'cyan'

class Player(GameObject):
  """fearless, human, player"""
  def __init__(self, world):
    super(Player, self).__init__(world)
    self.name = "Player"
    self.goal = None
    self.time_to_next_decision = 0
    self.speed = 200
    self.radius = 20
    self.color = 'blue'
    self.ammo = world.ammo.get()

class Zombie(GameObject):
  """zombies eat brains!!!""" 
  def __init__(self, world):
    super(Zombie, self).__init__(world)
    self.time_to_next_decision = 0
    self.name = "Zombie"
    self.target = self.world.player
    self.speed = 100
    self.radius = 10
    self.color = 'red'

class Medkit(GameObject):
  """Medkit"""
  def __init__(self, world):
    super(Medkit, self).__init__(world)
    self.name = "Medkit"
    self.amount = 1.0
    self.radius = 10
    self.color = 'green'

class Ammo(GameObject):
  """Ammo supply"""
  def __init__(self, world):
    super(Ammo, self).__init__(world)
    self.name = "Ammo"
    self.radius = 10
    self.color = 'black'

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

master = Tkinter.Tk()
master.title("2D Survival/Shooter Prototype with Micro-Director AI")

world = MicroDirector(CANVAS_WIDTH, CANVAS_WIDTH)
world.populate(final_brains.world_specification, final_brains.brain_classes)

canvas = Tkinter.Canvas(master, width=CANVAS_WIDTH, height=CANVAS_HEIGHT) 
canvas.grid(row=0, column=0)

SIMULATION_TICK_DELAY_MS = 20.0
GRAPHICS_TICK_DELAY_MS = 60.0

def global_simulation_tick():
  world.update(SIMULATION_TICK_DELAY_MS/1000.0)
  master.after(int(SIMULATION_TICK_DELAY_MS), global_simulation_tick)

def global_graphics_tick():
  world.draw(canvas)
  master.after(int(GRAPHICS_TICK_DELAY_MS), global_graphics_tick)

master.after_idle(global_simulation_tick)
master.after_idle(global_graphics_tick)

def left_button_down(event):
  world.sel_b = (event.x, event.y)
  if world.ammo.get():
    world.ammo.set(world.ammo.get() - 1)
    world.shoot()

def right_button_double(event):
  world.sel_a = (0,0)
  world.sel_b = (world.width, world.height)
  world.make_selection()

def right_button_move(event):
  if world.sel_a:
    world.sel_b = (event.x, event.y)

def right_button_up(event):
  if world.sel_a:
    world.sel_b = (event.x, event.y)
    world.make_selection()

def right_button_down(event):
  world.issue_selection_order((event.x, event.y))

def key_down(event):
  world.issue_selection_order(event.char)

master.bind('<ButtonPress-1>', left_button_down)
master.bind('<Double-Button-2>', right_button_double)
master.bind('<Double-Button-3>', right_button_double)
master.bind('<B2-Motion>', right_button_move)
master.bind('<B3-Motion>', right_button_move)
master.bind('<ButtonRelease-2>', right_button_up)
master.bind('<ButtonRelease-3>', right_button_up)
master.bind('<ButtonPress-2>', right_button_down)
master.bind('<ButtonPress-3>', right_button_down)
master.bind('<Key>', key_down)
master.bind('<Escape>', lambda event: master.quit())

master.mainloop()
