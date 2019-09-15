class Robot:
    def __init__(self, id):
        self.id = id
        self.inside = True
        self.goalScored = 0
        self.walked = 0
        self.shoot = 0
        self.passing = 0


class Team:
    def __init__(self):
        self.score = 0
        self.name = 'BLANK'
        self.county = 'NOWHERE'
        self.info = {}
        self.side = 'LEFT'
        self.robots = [Robot(i) for i in range(5)]
        self.goalkick = []
        self.corner = []
        self.ballPossessionOverall = 0
        self.ballPossessionMidterm = 0


class Context:
    def __init__(self):
        self.time_passed = 0
        self.time_left = 0
        self.stage = 'NONE'
        self.teamA = Team()
        self.teamB = Team()
        self.ballInLeftAreaCycle = 0
        self.ballInRightAreaCycle = 0
        self.ballInCenterAreaCycle = 0
        self.RobotTouchBall = (-1, -1)
        self.lastRobotTouchBall = (-1, -1)
