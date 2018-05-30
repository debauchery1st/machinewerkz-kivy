

#      o o
#    o o
def shape1a(x, y, di):
    h = (x, y-di, di, di)
    i = (x, y, di, di)
    j = (x+di, y, di, di)
    k = (x+di, y+di, di, di)
    return h, i, j, k


def shape1b(x, y, di):
    h = (x+di, y, di, di)
    i = (x, y, di, di)
    j = (x-di, y+di, di, di)
    k = (x, y+di, di, di)
    return h, i, j, k


def shape1c(x, y, di):
    return shape1a(x, y, di)


def shape1d(x, y, di):
    return shape1b(x, y, di)


#   o o o o
def shape2a(x, y, di):
    h = (x, y, di, di)
    i = (x, y + di, di, di)
    j = (x, y + di*2, di, di)
    k = (x, y + di*3, di, di)
    return h, i, j, k


def shape2b(x, y, di):
    h = (x, y, di, di)
    i = (x + di, y, di, di)
    j = (x + di*2, y, di, di)
    k = (x + di*3, y, di, di)
    return h, i, j, k


def shape2c(x, y, di):
    return shape2a(x, y, di)


def shape2d(x, y, di):
    return shape2b(x, y, di)


#   o o o
#   o
def shape3a(x, y, di):
    h = (x, y, di, di)
    i = (x, y + di, di, di)
    j = (x, y + di*2, di, di)
    k = (x+di, y + di*2, di, di)
    return h, i, j, k


def shape3b(x, y, di):
    h = (x, y, di, di)
    i = (x + di, y, di, di)
    j = (x + di*2, y, di, di)
    k = (x, y+di, di, di)
    return h, i, j, k


def shape3c(x, y, di):
    h = (x+di, y, di, di)
    i = (x, y, di, di)
    j = (x+di, y + di, di, di)
    k = (x+di, y + di*2, di, di)
    return h, i, j, k


def shape3d(x, y, di):
    h = (x, y+di, di, di)
    i = (x + di, y+di, di, di)
    j = (x + di*2, y+di, di, di)
    k = (x + di*2, y, di, di)
    return h, i, j, k


#     o o
#     o o
def shape4a(x, y, di):
    h = (x, y, di, di)
    i = (x, y + di, di, di)
    j = (x+di, y, di, di)
    k = (x+di, y + di, di, di)
    return h, i, j, k


def shape4b(x, y, di):
    return shape4a(x, y, di)


def shape4c(x, y, di):
    return shape4a(x, y, di)


def shape4d(x, y, di):
    return shape4a(x, y, di)


#    o o
#      o o
def shape5a(x, y, di):
    h = (x+di, y, di, di)
    i = (x, y+di, di, di)
    j = (x+di, y+di, di, di)
    k = (x, y+di*2, di, di)
    return h, i, j, k


def shape5b(x, y, di):
    h = (x, y+di, di, di)
    i = (x+di, y+di, di, di)
    j = (x+di, y+di*2, di, di)
    k = (x+di*2, y+di*2, di, di)
    return h, i, j, k


def shape5c(x, y, di):
    return shape5a(x, y, di)


def shape5d(x, y, di):
    return shape5b(x, y, di)


#     o
#   o o o

def shape6a(x, y, di):
    h = (x, y, di, di)
    i = (x+di, y, di, di)
    j = (x+di*2, y, di, di)
    k = (x+di, y + di, di, di)
    return h, i, j, k


def shape6b(x, y, di):
    h = (x, y, di, di)
    i = (x + di, y-di, di, di)
    j = (x + di, y, di, di)
    k = (x + di, y+di, di, di)
    return h, i, j, k


def shape6c(x, y, di):
    h = (x, y, di, di)
    i = (x+di, y, di, di)
    j = (x+di*2, y, di, di)
    k = (x+di, y - di, di, di)
    return h, i, j, k


def shape6d(x, y, di):
    h = (x+di, y, di, di)
    i = (x, y-di, di, di)
    j = (x, y, di, di)
    k = (x, y+di, di, di)
    return h, i, j, k


#   o o o
#       o
def shape7a(x, y, di):
    h = (x+di, y, di, di)
    i = (x+di, y + di, di, di)
    j = (x+di, y + di*2, di, di)
    k = (x, y + di*2, di, di)
    return h, i, j, k


def shape7b(x, y, di):
    h = (x, y, di, di)
    i = (x, y+di, di, di)
    j = (x + di, y+di, di, di)
    k = (x + di*2, y+di, di, di)
    return h, i, j, k


def shape7c(x, y, di):
    h = (x, y, di, di)
    i = (x+di, y, di, di)
    j = (x, y + di, di, di)
    k = (x, y + di*2, di, di)
    return h, i, j, k


def shape7d(x, y, di):
    h = (x, y, di, di)
    i = (x+di, y, di, di)
    j = (x+di*2, y, di, di)
    k = (x+di*2, y+di, di, di)
    return h, i, j, k


def get_shape(x, y, SU, state, _shape):
    SHAPETRIX = [
        [shape1a, shape1b, shape1c, shape1d],
        [shape2a, shape2b, shape2c, shape2d],
        [shape3a, shape3b, shape3c, shape3d],
        [shape4a, shape4b, shape4c, shape4d],
        [shape5a, shape5b, shape5c, shape5d],
        [shape6a, shape6b, shape6c, shape6d],
        [shape7a, shape7b, shape7c, shape7d],
    ]
    choice = _shape % (len(SHAPETRIX)) if _shape > 0 else 0
    rotation = state % 4
    # print(choice, rotation)
    try:
        h, i, j, k = SHAPETRIX[choice][rotation](x, y, SU)
    except IndexError as e:
        print("FORGET SOMETHING?")
        raise e
    xs = [h[0], i[0], j[0], k[0], x]
    ys = [h[1], i[1], j[1], k[1], y]
    low = max(ys)
    high = min(ys) - SU
    left = min(xs)
    right = max(xs) + SU
    return h, i, j, k, low, high, left, right

