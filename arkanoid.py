__author__ = 'Maxim'

import simpleguitk as simplegui
from simpleguitk.canvas import Canvas
from simpleguitk.frame import Frame
import math

class Rect(object):
    """
    x1,y1 -> #--------+
             |        |
             +--------#  <- x2,y2
    """

    def __init__(self, x1, y1, x2, y2, fill_color="white", border_width=0, border_color=""):
        self.border_color = border_color or fill_color
        self.border_width = border_width
        self.fill_color = fill_color
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def draw(self, canvas):
        canvas.draw_polygon(
            [[self.x1, self.y1], [self.x1, self.y2], [self.x2, self.y2], [self.x2, self.y1]],
            self.border_width,
            self.border_color,
            self.fill_color
        )


class Circle(object):

    def __init__(self, pos_x, pos_y, radius=2,
                 fill_color="white", border_width=0, border_color=""):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.radius = radius
        self.border_color = border_color or fill_color
        self.border_width = border_width
        self.fill_color = fill_color

    def draw(self, canvas):
        canvas.draw_circle([self.pos_x, self.pos_y], self.radius,
                           self.border_width, self.border_color, self.fill_color)


class MovableMixin(object):

    def set_velocity(self, vel_x, vel_y, max_vel=10):
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.max_vel = max_vel

    def set_acceleration(self, acc=0.0, max_acc=1):
        self.acc = acc
        self.max_acc = max_acc

    def calc_velocity(self):
        if self.vel_x+self.vel_y:
            self.vel_x += self.acc * self.vel_x/(self.vel_x+self.vel_y)
            self.vel_y += self.acc * self.vel_y/(self.vel_x+self.vel_y)
        else:
            self.vel_x += self.acc / 2
            self.vel_y += self.acc / 2
        total_velocity = self.calc_total_velocity()
        if total_velocity > self.max_vel:
            self.acc = 0
            brake = self.max_vel/total_velocity
            self.vel_x *= brake
            self.vel_y *= brake

    def calc_total_velocity(self):
        return math.sqrt(self.vel_x*self.vel_x + self.vel_y*self.vel_y)

    def get_point_pos(self, point):
        return point[0] + self.vel_x, point[1] + self.vel_y

    def move_point(self, point, game):
        self.calc_velocity()
        ox, oy = map(int, point)
        nx, ny = self.get_point_pos(point)
        # x_game_objects = set()
        # y_game_objects = set()
        # for x in range(ox, int(nx)+1):
        #     x_game_objects = x_game_objects | set(game.matrix_x[x])
        # for y in range(oy, int(ny)+1):
        #     y_game_objects = y_game_objects | set(game.matrix_y[y])
        # game_objects = list(x_game_objects & y_game_objects)
        # print game_objects
        # if len(game_objects):
        #     print self
        #     print game_objects
        #     raise
        return nx, ny

class Ball(MovableMixin, Circle):
    def __init__(self, pos_x, pos_y, vel_x=0.0, vel_y=0.0, acc=0.0, *args, **kwargs):
        super(Ball, self).__init__(pos_x, pos_y, *args, **kwargs)
        self.set_velocity(vel_x, vel_y)
        self.set_acceleration(acc)

    def move(self, game):
        self.pos_x, self.pos_y = super(Ball, self).move_point([self.pos_x, self.pos_y], game)


class Game(object):

    WIDTH = 600
    HEIGHT = 800
    WALL_WIDTH = 10

    def __init__(self):
        self.pressed_keys = []
        self.objects = []
        self.balls = []
        self.matrix_x = {x: [] for x in range(0, self.WIDTH+1)}
        self.matrix_y = {y: [] for y in range(0, self.HEIGHT+1)}

    def render(self, canvas):
        for obj in self.objects:
            obj.draw(canvas)

        for obj in self.balls:
            obj.move(self)
            obj.draw(canvas)

    def init_walls(self):
        self.add_object(Rect(0, 0, self.WALL_WIDTH, self.HEIGHT, "grey"))
        self.add_object(Rect(self.WIDTH, 0,  self.WIDTH-self.WALL_WIDTH, self.HEIGHT, "grey"))
        self.add_object(Rect(0, 0, self.WIDTH, self.WALL_WIDTH, "grey"))

    def init_ball(self):
        self.add_ball(Ball(30, 30, vel_x=0, vel_y=1, acc=0.5))
        self.add_ball(Ball(30, 50, vel_x=1, vel_y=0, acc=0.05))
        self.add_ball(Ball(30, 50, vel_x=0.5, vel_y=0.5, acc=0.05))

    def key_up(self, key):
        if key not in self.pressed_keys:
            self.pressed_keys.append(key)

    def key_down(self, key):
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def add_object(self, obj):
        if obj not in self.objects:
            self.objects.append(obj)
            for x in range(obj.x1, obj.x2+1):
                if obj not in self.matrix_x[x]:
                    self.matrix_x[x].append(obj)
            for y in range(obj.y1, obj.y2+1):
                if obj not in self.matrix_y[y]:
                    self.matrix_y[y].append(obj)

    def remove_obj(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)
            for x in range(obj.x1, obj.x2+1):
                if obj in self.matrix_x[x]:
                    self.matrix_x[x].remove(obj)
            for y in range(obj.y1, obj.y2+1):
                if obj in self.matrix_y[y]:
                    self.matrix_y[y].remove(obj)

    def add_ball(self, obj):
        self.balls.append(obj)


if __name__ == "__main__":

    game = Game()
    game.init_walls()
    game.init_ball()

    frame = simplegui.create_frame("Arkanoid", game.WIDTH, game.HEIGHT)
    frame.set_draw_handler(game.render)
    frame.set_keydown_handler(game.key_up)
    frame.set_keyup_handler(game.key_down)
    frame.start()

