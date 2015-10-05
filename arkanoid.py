__author__ = 'Maxim'

try:
    import simplegui
except ImportError:
    import simpleguitk as simplegui
import math
from random import random

def line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, -C


def intersection(L1, L2):
    D  = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x,y
    else:
        return False


class Rect(object):
    """
    x1,y1 -> #--------+
             |        |
             +--------#  <- x2,y2
    """

    def __init__(self, x1, y1, x2, y2, fill_color="white", border_width=0.1, border_color=""):
        self.border_color = border_color or fill_color
        self.border_width = border_width
        self.fill_color = fill_color
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def sides(self):
        return [
            [[self.x1, self.y1], [self.x1, self.y2]],
            [[self.x1, self.y2], [self.x2, self.y2]],
            [[self.x2, self.y2], [self.x2, self.y1]],
            [[self.x2, self.y1], [self.x1, self.y1]],
        ]

    def draw(self, canvas):
        canvas.draw_polygon(
            [[self.x1, self.y1], [self.x1, self.y2], [self.x2, self.y2], [self.x2, self.y1]],
            self.border_width,
            self.border_color,
            self.fill_color
        )

    def __repr__(self):
        return "Rect(%s,%s,%s,%s <%s>)" % (self.x1, self.y1, self.x2, self.y2, id(self))


class Circle(object):

    def __init__(self, pos_x, pos_y, radius=2,
                 fill_color="white", border_width=0.1, border_color=""):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.radius = radius
        self.border_color = border_color or fill_color
        self.border_width = border_width
        self.fill_color = fill_color

    def draw(self, canvas):
        canvas.draw_circle([self.pos_x, self.pos_y], self.radius,
                           self.border_width, self.border_color, self.fill_color)

    def __repr__(self):
        return "Circle(%s,%s,%s <%s>)" % (self.pos_x, self.pos_y, self.radius, id(self))


class MovableMixin(object):

    def set_direction(self, dir):
        # prevent items from moving in trajectories near strict vertical and stric horizontal
        if -1 <= dir <= 1 or 179 <= dir <= 181 or 89 <= dir <= 91 or 269 <= dir <= 271:
            dir += (0.5 - random()) * 4
        self.dir = dir
        self.dir_rad = math.radians(dir)
        self.cos_dir = float("%0.5f" % math.cos(self.dir_rad))
        self.sin_dir = float("%0.5f" % math.sin(self.dir_rad))

    def set_velocity(self, velocity, direction, max_vel=9):
        self.vel = velocity
        self.max_vel = max_vel
        self.set_direction(direction)

    def set_acceleration(self, acc=0.0, max_acc=1):
        self.acc = acc
        self.max_acc = max_acc

    def calc_velocity(self):
        self.vel += self.acc
        # total_velocity = self.calc_total_velocity()
        if self.vel > self.max_vel:
            self.acc = 0
            self.vel = self.max_vel

    # def calc_total_velocity(self):
    #     return math.sqrt(self.vel_x**2 + self.vel_y**2)

    def get_point_pos(self, point):
        dx = self.cos_dir * self.vel
        dy = self.sin_dir * self.vel
        return point[0] + dx, point[1] + dy

    def move_point(self, point, game):
        self.calc_velocity()
        ox, oy = map(int, point)
        nx, ny = self.get_point_pos(point)

        lx = int(min(ox, nx))
        rx = int(max(ox, nx))
        ly = int(min(oy, ny))
        ry = int(max(oy, ny))

        x_game_objects = set()
        y_game_objects = set()

        for x in range(lx, rx+1):
            # x_game_objects = x_game_objects | set(game.matrix_x[x])
            x_game_objects = x_game_objects.union(game.matrix_x[x])

        for y in range(ly, ry+1):
            # y_game_objects = y_game_objects | set(game.matrix_y[y])
            y_game_objects = y_game_objects.union(game.matrix_y[y])

        game_objects = list(x_game_objects.intersection(y_game_objects))

        if game_objects:
            intersections = []
            l1 = line([lx, ly], [rx, ry])
            for obj in game_objects:
                for side in obj.sides():
                    l2 = line(side[0], side[1])
                    point = intersection(l1, l2)
                    if point and lx <= point[0] <= rx and ly <= point[1] <= ry:
                        intersections.append([side, point])
            nearest_point_dist = max(game.width, game.height)
            nearest_point = None
            for side, point in intersections:
                dist = math.hypot(point[0] - lx, point[1] - ly)
                if dist < nearest_point_dist:
                    nearest_point = (side, point)

            if nearest_point:
                nx, ny = nearest_point[1]
                side = nearest_point[0]

                if side[0][0] == side[1][0]:
                    # vertical side
                    self.set_direction((180 - self.dir) % 360)
                    if 270 <= self.dir < 360 or 0 <= self.dir < 90:
                        nx += 1
                    else:
                        nx -= 1
                if side[0][1] == side[1][1]:
                    self.set_direction((360 - self.dir) % 360)
                    if 0 <= self.dir < 180:
                        ny += 1
                    else:
                        ny -= 1
        if not 0 < nx < game.width-1 or not 0 < ny < game.height-1:
            self.destroy(game)

        return nx, ny

    def destroy(self, game):
        print "DESTROY: %s" % self
        if self in game.balls:
            game.balls.remove(self)


class Ball(MovableMixin, Circle):
    def __init__(self, pos_x, pos_y, velocity=0.0, direction=0.0, acc=0.0, *args, **kwargs):

        # codesculptor has not `super` method =(
        # super(Ball, self).__init__(pos_x, pos_y, *args, **kwargs)
        Circle.__init__(self, pos_x, pos_y, *args, **kwargs)

        self.set_velocity(velocity, direction)
        self.set_acceleration(acc)

    def move(self, game):
        # self.pos_x, self.pos_y = super(Ball, self).move_point([self.pos_x, self.pos_y], game)
        self.pos_x, self.pos_y = MovableMixin.move_point(self, [self.pos_x, self.pos_y], game)

    def __repr__(self):
         return "Ball(%s,%s <%s>)" % (self.pos_x, self.pos_y, id(self))


class Game(object):
    
    WALL_WIDTH = 10
    TICK_INTERVAL = 1000
    frames = 0
    ticks = 0

    def __init__(self, width, height, frame):
        frame.add_label('--- ARKANOID ---')
        self.width = width
        self.height = height
        self.pressed_keys = []
        self.objects = []
        self.balls = []
        self.frame = frame
        self.timer = simplegui.create_timer(self.TICK_INTERVAL, self.tick)
        self.timer.start()
        self.label = frame.add_label('FPS: 0  ')

        self.matrix_x = {}
        for x in range(0, self.width+1):
            self.matrix_x[x] = []

        self.matrix_y = {}
        for y in range(0, self.height+1):
            self.matrix_y[y] = []

    def render(self, canvas):
        for obj in self.objects:
            obj.draw(canvas)

        if not self.balls:
            print "GAME OVER!"

        for obj in self.balls:
            obj.move(self)
            obj.draw(canvas)
        self.frames += 1

    def tick(self):
        self.label.set_text('FPS: %s  ' % self.get_fps())
        self.frames = 0

    def get_fps(self):
        return self.frames*1000/self.TICK_INTERVAL

    def init_walls(self):
        self.add_object(Rect(0, 0, self.WALL_WIDTH, self.height, "grey"))
        self.add_object(Rect(self.width, 0,  self.width-self.WALL_WIDTH, self.height, "grey"))
        self.add_object(Rect(0, 0, self.width, self.WALL_WIDTH, "grey"))

        # self.add_object(Rect(0, self.height,  self.width, self.height-self.WALL_WIDTH, "grey"))

        self.add_object(Rect(100, 100, self.WALL_WIDTH+100, self.height-100, "grey"))
        self.add_object(Rect(self.width-100, 100,  self.width-self.WALL_WIDTH-100, self.height-100, "grey"))
        self.add_object(Rect(100, 100, self.width-100, self.WALL_WIDTH+100, "grey"))

        # self.add_object(Rect(100, self.height-100,  self.width-100, self.height-self.WALL_WIDTH-100, "grey"))

    def init_balls(self):
        for i, v in enumerate(range(0, 360, 4)):
            self.add_ball(Ball(game.width/2, game.height/2, velocity=1, direction=v, acc=0.001))

        for i in range(0, 360, 20):
            self.add_ball(Ball(50, 50, velocity=1, direction=i, acc=0.001))

    def key_up(self, key):
        if key not in self.pressed_keys:
            self.pressed_keys.append(key)

    def key_down(self, key):
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def add_object(self, obj):
        if obj not in self.objects:
            self.objects.append(obj)
            for x in range(min(obj.x1, obj.x2), max(obj.x1, obj.x2)+1):
                if obj not in self.matrix_x[x]:
                    self.matrix_x[x].append(obj)
            for y in range(min(obj.y1, obj.y2), max(obj.y1, obj.y2)+1):
                if obj not in self.matrix_y[y]:
                    self.matrix_y[y].append(obj)

    def remove_obj(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)
            for x in range(min(obj.x1, obj.x2), max(obj.x1, obj.x2)+1):
                if obj in self.matrix_x[x]:
                    self.matrix_x[x].remove(obj)
            for y in range(min(obj.y1, obj.y2), max(obj.y1, obj.y2)+1):
                if obj in self.matrix_y[y]:
                    self.matrix_y[y].remove(obj)

    def add_ball(self, obj):
        self.balls.append(obj)


if __name__ == "__main__":

    WIDTH = 800
    HEIGHT = 800

    frame = simplegui.create_frame("Arkanoid", WIDTH, HEIGHT)
    game = Game(WIDTH, HEIGHT, frame)
    game.init_walls()
    game.init_balls()

    frame.set_draw_handler(game.render)
    frame.set_keydown_handler(game.key_up)
    frame.set_keyup_handler(game.key_down)
    frame.start()

