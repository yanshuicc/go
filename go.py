# coding:utf-8
# 围棋界面
import pygame
from pygame.locals import *
import sys
import copy
import utils

CLICK = USEREVENT + 1

BLACK = 100
WHITE = 101
RED = 102
GREY = 103
LIGHTGRAY = 104

GAME_START = 200
GAME_PAUSE = 201
GAME_END = 202
SGF_START = 210
SGF_PAUSE = 211
SGF_STOP = 212

INVFONT = 301
FONT2 = 302

pygame.init()
fonts = {
	FONT2: pygame.font.Font('./resources/mnjdy.ttf', 18)
}


colors = {
	BLACK: (0, 0, 0),
	RED: (255, 0, 0),
	GREY:	(190, 190, 190),
	LIGHTGRAY:(211, 211, 211),
	WHITE: (255, 255, 255)
}

blackChess = 1
whiteChess = 2
icon = 0
textures = {
	blackChess: pygame.image.load('./resources/blackChess.png'),
	whiteChess: pygame.image.load('./resources/whiteChess.png'),
	icon: pygame.image.load('./resources/yscc.ico')
}

INPUT = 250
NOTIN = 251

class CmdPanel(object):
	def __init__(self):
		# 辅助tab自动补全cmd的两个成员变量
		self.cmdSave = ''
		self.tabCount = 1
		# 显示的命令
		self.cmd = ''
		# 命令信息
		self.cmdInfo = ''
		# 命令状态
		self.status = NOTIN
		# 命令字典{'cmd':{'cmdInfo': cmdInfo, 'cmdFunc': cmdFunc}}
		self.cmdDict = {}

	def keyEvent(self, event, go):
		if event.type == KEYDOWN:
			keypress = pygame.key.get_pressed()
			for i, val in enumerate(keypress):
				if val == 1:
					c = chr(i)
					if 'A' <= c <= 'Z' or 'a' <= c <= 'z' or '0' <= c <= '9':
						self.cmd += c
						self.cmdSave = self.cmd
					if i == K_TAB:
						self.match()
					if i == K_BACKSPACE:
						self.cmd = self.cmd[:len(self.cmd)-1]
						self.cmdSave = self.cmd
					if i == K_RETURN:
						if self.cmd not in self.cmdDict.keys():
							self.cmdInfo = 'error cmd:'+ self.cmd
							self.tabCount = 1
							self.cmd = ''
						else:
							self.cmdInfo = self.cmdDict[self.cmd]['cmdInfo']
							self.cmdDict[self.cmd]['cmdFunc'](go)
							self.cmd = ''

	def match(self):
		cmds = self.cmdDict.keys()
		cmdlen = len(self.cmdSave)
		count = 0
		for cmd in cmds:
			if self.cmdSave == cmd[:cmdlen]:
				count += 1
				if count == self.tabCount:
					self.cmd = cmd
					self.tabCount += 1

	def drawText(self, screen, text, x, y, color=BLACK):
		textObj = fonts[FONT2].render(text, True, colors[color], colors[GREY])
		screen.blit(textObj, (x, y))

	def update(self, screen):
		self.drawText(screen, self.cmdInfo, 650, 400, RED)
		self.drawText(screen, self.cmd, 650, 480)

	def addKeyDict(self, key, value):
		self.cmdDict[key] = value

def cmdinit(cmdPanel):
	def helpCmd(go):
		go.goPanel.sgfStatus = SGF_START
		pass
	help = 'help：load，'
	helpValue = {'cmdInfo': help, 'cmdFunc': helpCmd}
	cmdPanel.addKeyDict('help', helpValue)

	def loadCmd(go):
		go.goPanel.sgfStatus = SGF_START
		pass
	loadValue = {'cmdInfo': '加载文件', 'cmdFunc': loadCmd}
	cmdPanel.addKeyDict('load', loadValue)

	def restartCmd(go):
		pass


class GoPanel(object):
	def __init__(self):
		# 棋盘格子数
		self.board_size = 19
		# 棋盘的边界距
		self.posX = 40
		self.posY = 40
		# 每一个格子的大小
		self.tileSize = 30
		self.htileSize = self.tileSize / 2
		# 棋盘
		self.tiles = [[0 for _ in range(0, self.board_size)] for _ in range(0, self.board_size)]
		# 下棋顺序
		self.tilesOrder = [[0 for _ in range(0, self.board_size)] for _ in range(0, self.board_size)]
		self.orderCount = 0
		# 棋盘大小
		self.w = self.board_size * self.tileSize
		self.h = self.board_size * self.tileSize
		# 鼠标位置
		self.mouseX = 0
		self.mouseY = 0
		# 黑白棋执手 黑棋为1 白棋为2
		self.flag = 1
		# 黑棋数目
		self.blackChessCount = 0
		# 白棋数目
		self.whiteChessCount = 0
		# 贴目
		self.komi = 6.5
		# 让子
		self.handicap = 0
		# 胜负结果
		self.result = ''
		# sgf 节点
		self.sgfNode = None
		# sgf 状态
		self.sgfStatus = SGF_STOP

		self.info1 = ''
		self.info2 = ''
		self.info3 = ''

	def getPos(self, pos):
		return (pos[0] - self.posX + self.htileSize,
				pos[1] - self.posY +self.htileSize)

	def update(self,screen):
		for x in range(0, self.board_size):
			for y in range(0, self.board_size):
				pygame.draw.line(screen, colors[BLACK],
								 (self.posX + x * self.tileSize, self.posY + y * self.tileSize), (self.posX + x * self.tileSize, self.posY + y))
				pygame.draw.line(screen, colors[BLACK],
								 (self.posX + x * self.tileSize, self.posY + y * self.tileSize), (self.posX + x, self.posY + y * self.tileSize))

		for x in range(0, self.board_size):
			for y in range(0, self.board_size):
				if self.tiles[x][y] == 1:
					pos = (int(self.posX + x*self.tileSize), int(self.posY + y*self.tileSize))
					pygame.draw.circle(screen, colors[BLACK],
									   pos, int(self.htileSize))
				if self.tiles[x][y] == 2:
					pos = (int(self.posX + x * self.tileSize), int(self.posY + y * self.tileSize))
					pygame.draw.circle(screen, colors[GREY],
									   pos, int(self.htileSize))
		self.drawRedCircle(screen)

	def drawRedCircle(self, screen):
		pos = (int(self.mouseX*self.tileSize)+self.posX, int(self.mouseY * self.tileSize)+self.posY)
		pygame.draw.circle(screen, colors[RED],
						   pos, int(self.htileSize), 1)

	def mouseEvent(self, event):
		if event.type == MOUSEMOTION:
			pos = self.getPos(event.dict['pos'])
			if int(pos[0] / self.tileSize) < self.board_size:
				self.mouseX = int(pos[0] / self.tileSize)
			elif int(pos[0] / self.tileSize) > self.board_size:
				self.mouseX = self.board_size - 1
			if int(pos[1] / self.tileSize) < self.board_size:
				self.mouseY = int(pos[1] / self.tileSize)
			elif int(pos[1] / self.tileSize) > self.board_size:
				self.mouseY = self.board_size - 1

			tiles = copy.deepcopy(self.tiles)
			flag = tiles[self.mouseX][self.mouseY]
			if flag == 1:
				self.info1 = '当前棋子颜色：黑'
				self.info2 = '当前棋子坐标：('+str(self.mouseX)+','+str(self.mouseY)+')'
				self.info3 = '当前棋子活：'+str(self.judgeOne(self.mouseX, self.mouseY, flag, tiles))
			if flag == 2:
				self.info1 = '当前棋子颜色：白'
				self.info2 = '当前棋子坐标：('+str(self.mouseX)+','+str(self.mouseY)+')'
				self.info3 = '当前棋子活：'+str(self.judgeOne(self.mouseX, self.mouseY, flag, tiles))
		elif event.type == MOUSEBUTTONUP:
			if event.button == 1:
				pos = self.getPos(event.dict['pos'])
				# 判断鼠标位置在棋盘上
				if 0 <= int(pos[0] / self.tileSize) < self.board_size and 0 <= int(pos[1] / self.tileSize) < self.board_size:
					self.addStone((self.mouseX, self.mouseY), self.flag)

	# 落子
	def addStone(self, pos, color):
		if self.tiles[pos[0]][pos[1]] == 0:
			self.tiles[pos[0]][pos[1]] = color
			tiles = copy.deepcopy(self.tiles)
			if color == blackChess:
				self.flag = color = whiteChess
				self.blackChessCount += 1
			elif color == whiteChess:
				self.flag = color = blackChess
				self.whiteChessCount += 1
			X = [(0,1),(1,0),(0,-1),(-1,0)]
			for x in X:
				if 0 <= pos[0]+ x[0] < self.board_size and \
					0 <= pos[1] + x[1] < self.board_size:
					if self.tiles[pos[0] + x[0]][pos[1] + x[1]] == color:
						if self.judgeOne(pos[0] + x[0], pos[1] + x[1], color, tiles) == 0:
							self.removeArea(pos[0] + x[0], pos[1] + x[1], color)

	def judgeOne(self, x, y, flag, tiles):
		# 判断过的区域置为负数，不再重复判断
		tiles[x][y] = -1 * flag
		i = 0
		if x - 1 >= 0:
			if tiles[x - 1][y] == 0:
				i += 1
			elif tiles[x - 1][y] == flag:
				i += self.judgeOne(x - 1, y, flag, tiles)
		if x + 1 < self.board_size:
			if tiles[x + 1][y] == 0:
				i += 1
			elif tiles[x + 1][y] == flag:
				i += self.judgeOne(x + 1, y, flag, tiles)
		if y - 1 >= 0:
			if tiles[x][y - 1] == 0:
				i += 1
			elif tiles[x][y - 1] == flag:
				i += self.judgeOne(x, y - 1, flag, tiles)
		if y + 1 < self.board_size:
			if tiles[x][y + 1] == 0:
				i += 1
			elif tiles[x][y + 1] == flag:
				i += self.judgeOne(x, y + 1, flag, tiles)
		return i

	def removeArea(self, x, y, flag):
		if self.tiles[x][y] != flag:
			return
		self.tiles[x][y] = 0
		if x - 1 >= 0:
			if self.tiles[x - 1][y] == flag:
				self.removeArea(x - 1, y, flag)
		if x + 1 < self.board_size:
			if self.tiles[x + 1][y] == flag:
				self.removeArea(x + 1, y, flag)
		if y - 1 >= 0:
			if self.tiles[x][y - 1] == flag:
				self.removeArea(x, y - 1, flag)
		if y + 1 < self.board_size:
			if self.tiles[x][y + 1] == flag:
				self.removeArea(x, y + 1, flag)

	def loadSGF(self, filename):
		with open(filename) as f:
			node = utils.init_sgf(self, f.read())
			self.sgfNode = node

	def nextNode(self):
		self.sgfNode = utils.replay_sgf(self, self.sgfNode)



class Go(object):
	def __init__(self):
		self.windowWidth = 900
		self.windowHeight = 600
		self.goPanel = GoPanel()
		self.cmdPanel = CmdPanel()
		cmdinit(self.cmdPanel)
		self.status = GAME_PAUSE
		self.DISPLAYSURF = pygame.display.set_mode((900, 600))
		self.fpsClock = pygame.time.Clock()

	def drawText(self, screen, text, x, y):
		textObj = fonts[FONT2].render(text, True, colors[BLACK], colors[GREY])
		screen.blit(textObj, (x, y))

	def update(self):
		self.fpsClock.tick(24)
		self.DISPLAYSURF.fill(colors[WHITE])
		self.goPanel.update(self.DISPLAYSURF)
		self.cmdPanel.update(self.DISPLAYSURF)
		self.drawText(self.DISPLAYSURF, '黑子总数:' + str(self.goPanel.blackChessCount), 650, 40)
		self.drawText(self.DISPLAYSURF, '白子总数:' + str(self.goPanel.whiteChessCount), 650, 80)
		self.drawText(self.DISPLAYSURF, self.goPanel.info1, 650, 120)
		self.drawText(self.DISPLAYSURF, self.goPanel.info2, 650, 160)
		self.drawText(self.DISPLAYSURF, self.goPanel.info3, 650, 200)
		pygame.draw.rect(self.DISPLAYSURF,
						 colors[RED],
						(0, 0, self.windowWidth, self.windowHeight),2)
		pygame.display.update()

	def mouseEvent(self, event):
		self.goPanel.mouseEvent(event)

	def keyEvent(self, event):
		self.cmdPanel.keyEvent(event, self)

	def exit(self):
		pygame.quit()
		sys.exit()


if __name__ == "__main__":
	game = Go()
	pygame.display.set_caption("Yscc-Surrender")
	pygame.display.set_icon(textures[icon])
	pygame.time.set_timer(CLICK, 1000)
	game.goPanel.loadSGF('data/2017-04-01-1.sgf')
	while True:
		game.update()
		for event in pygame.event.get():
			print(event)
			if event.type == QUIT:
				game.exit()
			if event.type == MOUSEMOTION or event.type == MOUSEBUTTONDOWN or event.type == MOUSEBUTTONUP:
				game.mouseEvent(event)
			if event.type == KEYDOWN:
				game.keyEvent(event)
			if event.type == CLICK:
				if game.goPanel.sgfStatus == SGF_START:
					game.goPanel.nextNode()
				if game.goPanel.sgfStatus == SGF_STOP:
					pass

