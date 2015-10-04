__author__ = 'Maxim'
import simpleguitk as simplegui
import random
import math
# initialize globals - pos and vel encode vertical info for paddles
WIDTH = 600
HEIGHT = 400
BALL_RADIUS = 20
PAD_WIDTH = 8
PAD_HEIGHT = 80
HALF_PAD_WIDTH = PAD_WIDTH / 2
HALF_PAD_HEIGHT = PAD_HEIGHT / 2
ACCEL_COEF = 1.1   # X acceleration after each paddle collision
PADDLE_COEF = 0.33  # Y speed transmitted to ball from paddle
RIGHT = True
LEFT = False
ball_pos = [WIDTH / 2, HEIGHT / 2]
ball_vel = [3, 3]
paddle1_pos = 160
paddle2_pos = 160
paddle1_vel = 0
paddle2_vel = 0
count_left = 0
count_right = 0
direction = random.choice([LEFT, RIGHT])

# initialize ball_pos and ball_vel for new bal in middle of table
# if direction is RIGHT, the ball's velocity is upper right, else upper left

def spawn_ball(direction):
    global ball_pos, ball_vel  # these are vectors stored as lists
    ball_pos = [WIDTH / 2, HEIGHT / 2]

    if direction == RIGHT:
        ball_vel = [random.randrange(2, 4), - (random.randrange(1, 3))]
    elif direction == LEFT:
        ball_vel = [-(random.randrange(2, 4)), - (random.randrange(1, 3))]

        # define event handlers


def new_game():
    global paddle1_pos, paddle2_pos, paddle1_vel, paddle2_vel  # these are numbers
    global count_left, count_right  # these are ints
    spawn_ball(direction)
    count_left = 0
    count_right = 0


def draw(canvas):
    global score1, score2, paddle1_pos, paddle2_pos, ball_pos, ball_vel, count_left, count_right

    # draw mid line and gutters
    canvas.draw_line([WIDTH / 2, 0], [WIDTH / 2, HEIGHT], 1, "White")
    canvas.draw_line([PAD_WIDTH, 0], [PAD_WIDTH, HEIGHT], 1, "White")
    canvas.draw_line([WIDTH - PAD_WIDTH, 0], [WIDTH - PAD_WIDTH, HEIGHT], 1, "White")

    # update ball
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]
    # draw ball
    canvas.draw_circle(ball_pos, BALL_RADIUS, 2, "Red", "White")
    # update paddle's vertical position, keep paddle on the screen

    if paddle1_pos + paddle1_vel < 0:
        paddle1_pos = 0
    elif paddle1_pos + paddle1_vel > HEIGHT - PAD_HEIGHT:
        paddle1_pos = HEIGHT - PAD_HEIGHT
    else:
        paddle1_pos += paddle1_vel

    if paddle2_pos + paddle2_vel < 0:
        paddle2_pos = 0
    elif paddle2_pos + paddle2_vel > HEIGHT - PAD_HEIGHT:
        paddle2_pos = HEIGHT - PAD_HEIGHT
    else:
        paddle2_pos += paddle2_vel

    # draw paddles
    canvas.draw_line([0, paddle1_pos], [0, paddle1_pos + PAD_HEIGHT], 14, "White")
    canvas.draw_line([600, paddle2_pos], [600, paddle2_pos + PAD_HEIGHT], 14, "White")
    # determine whether paddle and ball collide

    if ball_pos[0] <= BALL_RADIUS + PAD_WIDTH:
        if ball_pos[1] >= paddle1_pos and ball_pos[1] <= paddle1_pos + PAD_HEIGHT:
            ball_vel[0] = - ball_vel[0] * ACCEL_COEF
            ball_vel[1] += paddle1_vel * PADDLE_COEF
        else:
            print ball_pos, paddle1_pos
            spawn_ball(RIGHT)
            count_right += 1
    elif ball_pos[0] >= WIDTH - BALL_RADIUS - PAD_WIDTH:
        if ball_pos[1] >= paddle2_pos and ball_pos[1] <= paddle2_pos + PAD_HEIGHT:
            ball_vel[0] = - ball_vel[0] * ACCEL_COEF
            ball_vel[1] += paddle2_vel * PADDLE_COEF
        else:
            print ball_pos, paddle2_pos
            spawn_ball(LEFT)
            count_left += 1
    elif ball_pos[1] <= BALL_RADIUS:
        ball_vel[1] = - ball_vel[1]
    elif ball_pos[1] >= HEIGHT - BALL_RADIUS:
        ball_vel[1] = - ball_vel[1]


    # draw scores
    canvas.draw_text(str(count_left), (130, 70), 75, "Gray")
    canvas.draw_text(str(count_right), (430, 70), 75, "Gray")


def keydown(key):
    global paddle1_vel, paddle2_vel

    acc = 6
    if key == simplegui.KEY_MAP["w"]:
        paddle1_vel -= acc
    elif key == simplegui.KEY_MAP["s"]:
        paddle1_vel += acc
    elif key == simplegui.KEY_MAP["up"]:
        paddle2_vel -= acc
    elif key == simplegui.KEY_MAP["down"]:
        paddle2_vel += acc


def keyup(key):
    global paddle1_vel, paddle2_vel

    if key == simplegui.KEY_MAP["w"]:
        paddle1_vel = 0
    elif key == simplegui.KEY_MAP["s"]:
        paddle1_vel = 0
    elif key == simplegui.KEY_MAP["up"]:
        paddle2_vel = 0
    elif key == simplegui.KEY_MAP["down"]:
        paddle2_vel = 0


def reset():
    new_game()

# create frame
frame = simplegui.create_frame("Pong", WIDTH, HEIGHT)
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.add_button('Reset', reset, 50)


# start frame
new_game()
frame.start()
