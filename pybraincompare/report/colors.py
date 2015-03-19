'''
colors.py: part of pybraincompare package
Color stuffs

'''

import random

'''Generate N random colors'''
def random_colors(N):
  colors = []
  for x in range(0,N):
    r = lambda: random.randint(0,255)
    colors.append('#%02X%02X%02X' % (r(),r(),r()))
  return colors


