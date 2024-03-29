#!/usr/bin/python3

# Author(s): Luiz Felipe Vecchietti, Chansol Hong, Inbae Jeong
# Maintainer: Chansol Hong (cshong@rit.kaist.ac.kr)

from __future__ import print_function

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from autobahn.wamp.serializer import MsgPackSerializer
from autobahn.wamp.types import ComponentConfig
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

import argparse
import random
import sys

import base64
import numpy as np

# reset_reason
NONE = 0
GAME_START = 1
SCORE_MYTEAM = 2
SCORE_OPPONENT = 3
GAME_END = 4
DEADLOCK = 5
GOALKICK = 6
CORNERKICK = 7
PENALTYKICK = 8
HALFTIME = 9
EPISODE_END = 10

# game_state
STATE_DEFAULT = 0
STATE_KICKOFF = 1
STATE_GOALKICK = 2
STATE_CORNERKICK = 3
STATE_PENALTYKICK = 4

# coordinates
MY_TEAM = 0
OP_TEAM = 1
BALL = 2
X = 0
Y = 1
TH = 2
ACTIVE = 3
TOUCH = 4


class Received_Image(object):
  def __init__(self, resolution, colorChannels):
    self.resolution = resolution
    self.colorChannels = colorChannels
    # need to initialize the matrix at timestep 0
    self.ImageBuffer = np.zeros((resolution[1], resolution[0], colorChannels))  # rows, columns, colorchannels

  def update_image(self, received_parts):
    self.received_parts = received_parts
    for i in range(0, len(received_parts)):
      dec_msg = base64.b64decode(self.received_parts[i].b64, '-_')  # decode the base64 message
      np_msg = np.fromstring(dec_msg, dtype=np.uint8)  # convert byte array to numpy array
      reshaped_msg = np_msg.reshape((self.received_parts[i].height, self.received_parts[i].width, 3))
      for j in range(0, self.received_parts[i].height):  # y axis
        for k in range(0, self.received_parts[i].width):  # x axis
          self.ImageBuffer[j + self.received_parts[i].y, k + self.received_parts[i].x, 0] = reshaped_msg[
            j, k, 0]  # blue channel
          self.ImageBuffer[j + self.received_parts[i].y, k + self.received_parts[i].x, 1] = reshaped_msg[
            j, k, 1]  # green channel
          self.ImageBuffer[j + self.received_parts[i].y, k + self.received_parts[i].x, 2] = reshaped_msg[
            j, k, 2]  # red channel


class SubImage(object):
  def __init__(self, x, y, width, height, b64):
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.b64 = b64


class Frame(object):
  def __init__(self):
    self.time = None
    self.score = None
    self.reset_reason = None
    self.subimages = None
    self.coordinates = None


class Component(ApplicationSession):
  """
    AI Base + Commentator Skeleton
    """

  def __init__(self, config):
    ApplicationSession.__init__(self, config)

  def printConsole(self, message):
    print(message)
    sys.__stdout__.flush()

  def onConnect(self):
    self.join(self.config.realm)

  @inlineCallbacks
  def onJoin(self, details):

    ##############################################################################
    def init_variables(self, info):
      # Here you have the information of the game (virtual init() in random_walk.cpp)
      # List: game_time, number_of_robots
      #       field, goal, penalty_area, goal_area, resolution Dimension: [x, y]
      #       ball_radius, ball_mass,
      #       robot_size, robot_height, axle_length, robot_body_mass, ID: [0, 1, 2, 3, 4]
      #       wheel_radius, wheel_mass, ID: [0, 1, 2, 3, 4]
      #       max_linear_velocity, max_torque, codewords, ID: [0, 1, 2, 3, 4]
      # self.game_time = info['game_time']
      # self.number_of_robots = info['number_of_robots']

      self.field = info['field']
      self.goal = info['goal']
      # self.penalty_area = info['penalty_area']
      # self.goal_area = info['goal_area']
      self.resolution = info['resolution']

      # self.ball_radius = info['ball_radius']
      # self.ball_mass = info['ball_mass']

      # self.robot_size = info['robot_size']
      # self.robot_height = info['robot_height']
      # self.axle_length = info['axle_length']
      # self.robot_body_mass = info['robot_body_mass']

      # self.wheel_radius = info['wheel_radius']
      # self.wheel_mass = info['wheel_mass']

      # self.max_linear_velocity = info['max_linear_velocity']
      # self.max_torque = info['max_torque']
      # self.codewords = info['codewords']

      self.colorChannels = 3
      self.end_of_frame = False
      self.received_frame = Frame()
      self.image = Received_Image(self.resolution, self.colorChannels)
      return

    ##############################################################################

    try:
      info = yield self.call(u'aiwc.get_info', args.key)
    except Exception as e:
      self.printConsole("Error: {}".format(e))
    else:
      try:
        self.sub = yield self.subscribe(self.on_event, args.key)
      except Exception as e2:
        self.printConsole("Error: {}".format(e2))

    init_variables(self, info)

    try:
      yield self.call(u'aiwc.ready', args.key)
    except Exception as e:
      self.printConsole("Error: {}".format(e))
    else:
      self.printConsole("I am the commentator for this game!")

  @inlineCallbacks
  def on_event(self, f):

    @inlineCallbacks
    def set_comment(self, commentary):
      yield self.call(u'aiwc.commentate', args.key, commentary)
      return

    # initiate empty frame
    if (self.end_of_frame):
      self.received_frame = Frame()
      self.end_of_frame = False
    received_subimages = []

    if 'time' in f:
      self.received_frame.time = f['time']
    if 'score' in f:
      self.received_frame.score = f['score']
    if 'reset_reason' in f:
      self.received_frame.reset_reason = f['reset_reason']
    if 'half_passed' in f:
      self.received_frame.half_passed = f['half_passed']
    if 'ball_ownership' in f:
      self.received_frame.ball_ownership = f['ball_ownership']
    if 'subimages' in f:
      self.received_frame.subimages = f['subimages']
      # Uncomment following block to use images.
      # for s in self.received_frame.subimages:
      #     received_subimages.append(SubImage(s['x'],
      #                                        s['y'],
      #                                        s['w'],
      #                                        s['h'],
      #                                        s['base64'].encode('utf8')))
      # self.image.update_image(received_subimages)
    if 'coordinates' in f:
      self.received_frame.coordinates = f['coordinates']
    if 'EOF' in f:
      self.end_of_frame = f['EOF']
      # self.printConsole(self.received_frame.time)
      # self.printConsole(self.received_frame.score)
      # self.printConsole(self.received_frame.reset_reason)
      # self.printConsole(self.received_frame.half_passed)
      # self.printConsole(self.end_of_frame)

    if (self.end_of_frame):
      # self.printConsole("end of frame")

      if (self.received_frame.reset_reason == GAME_START):
        if (not self.received_frame.half_passed):
          set_comment(self, "Game has begun")
        else:
          set_comment(self, "Second half has begun")

      elif (self.received_frame.reset_reason == DEADLOCK):
        set_comment(self, "Position is reset since no one touched the ball")

      elif (self.received_frame.reset_reason == GOALKICK):
        set_comment(self, "A goal kick of Team {}".format("Red" if self.received_frame.ball_ownership else "Blue"))

      elif (self.received_frame.reset_reason == CORNERKICK):
        set_comment(self, "A corner kick of Team {}".format("Red" if self.received_frame.ball_ownership else "Blue"))

      elif (self.received_frame.reset_reason == PENALTYKICK):
        set_comment(self, "A penalty kick of Team {}".format("Red" if self.received_frame.ball_ownership else "Blue"))
      # To get the image at the end of each frame use the variable:
      # self.image.ImageBuffer

      if (self.received_frame.coordinates[BALL][X] >= (self.field[X] / 2) and abs(
        self.received_frame.coordinates[BALL][Y]) <= (self.goal[Y] / 2)):
        set_comment(self, "Team Red scored!!")
      elif (self.received_frame.coordinates[BALL][X] <= (-self.field[X] / 2) and abs(
        self.received_frame.coordinates[BALL][Y]) <= (self.goal[Y] / 2)):
        set_comment(self, "Team Blue scored!!")

      if (self.received_frame.reset_reason == HALFTIME):
        set_comment(self, "The halftime has met. Current score is: {} : {}".format(self.received_frame.score[0],
                                                                                   self.received_frame.score[1]))

      if (self.received_frame.reset_reason == EPISODE_END):
        if (self.received_frame.score[0] > self.received_frame.score[1]):
          set_comment(self, "Team Red won the game with score {} : {}".format(self.received_frame.score[0],
                                                                              self.received_frame.score[1]))
        elif (self.received_frame.score[0] < self.received_frame.score[1]):
          set_comment(self, "Team Blue won the game with score {} : {}".format(self.received_frame.score[1],
                                                                               self.received_frame.score[0]))
        else:
          set_comment(self, "The game ended in a tie with score {} : {}".format(self.received_frame.score[0],
                                                                                self.received_frame.score[1]))

      if (self.received_frame.reset_reason == GAME_END):
        if (self.received_frame.score[0] > self.received_frame.score[1]):
          set_comment(self, "Team Red won the game with score {} : {}".format(self.received_frame.score[0],
                                                                              self.received_frame.score[1]))
        elif (self.received_frame.score[0] < self.received_frame.score[1]):
          set_comment(self, "Team Blue won the game with score {} : {}".format(self.received_frame.score[1],
                                                                               self.received_frame.score[0]))
        else:
          set_comment(self, "The game ended in a tie with score {} : {}".format(self.received_frame.score[0],
                                                                                self.received_frame.score[1]))

        ##############################################################################
        # (virtual finish())
        # save your data
        with open(args.datapath + '/result.txt', 'w') as output:
          # output.write('yourvariables')
          output.close()
        # unsubscribe; reset or leave
        yield self.sub.unsubscribe()
        try:
          yield self.leave()
        except Exception as e:
          self.printConsole("Error: {}".format(e))
      ##############################################################################

      self.end_of_frame = False

  def onDisconnect(self):
    if reactor.running:
      reactor.stop()
