import random

# Agent J experiment generator: Barnsley fern / chaos game
random.seed(20260518)

rules = [
    (0.01, (0.0, 0.0, 0.0, 0.16, 0.0, 0.0)),
    (0.85, (0.85, 0.04, -0.04, 0.85, 0.0, 1.6)),
    (0.07, (0.20, -0.26, 0.23, 0.22, 0.0, 1.6)),
    (0.07, (-0.15, 0.28, 0.26, 0.24, 0.0, 0.44)),
]

x = y = 0.0
for _ in range(20):
    r = random.random()
    acc = 0.0
    for p, (a,b,c,d,e,f) in rules:
        acc += p
        if r <= acc:
            x, y = a*x + b*y + e, c*x + d*y + f
            break

for _ in range(10):
    r = random.random()
    acc = 0.0
    for p, (a,b,c,d,e,f) in rules:
        acc += p
        if r <= acc:
            x, y = a*x + b*y + e, c*x + d*y + f
            print(round(x, 4), round(y, 4))
            break
