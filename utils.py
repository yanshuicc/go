# coding:utf-8
import sgf
import time
import go

KGS_COLUMNS = 'ABCDEFGHJKLMNOPQRST'
SGF_COLUMNS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def init_sgf(panel, sgf_contents):
	'''
	Wrapper for sgf files, exposing contents as position_w_context instances
	with open(filename) as f:
		for position_w_context in replay_sgf(f.read()):
			print(position_w_context.position)
	'''
	collection = sgf.parse(sgf_contents)
	game = collection.children[0]
	props = game.root.properties
	assert int(sgf_prop(props.get('GM', ['1']))) == 1, "Not a Go SGF!"

	komi = 0
	handicap = 0
	board_size = 19
	result = ''
	if props.get('KM') != None:
		komi = float(sgf_prop(props.get('KM')))
		result=sgf_prop(props.get('RE'))
		handicap=int(sgf_prop(props.get('HA', [0])))
		board_size=int(sgf_prop(props.get('SZ')))

	panel.result = result
	panel.komi = komi
	panel.handicap = handicap
	panel.board_size = board_size

	current_node = game.root
	return current_node

def replay_sgf(panel, current_node):
	if panel is not None and current_node is not None:
		pos = handle_node(panel, current_node)
		# maybe_correct_next(pos, current_node.next)
		current_node = current_node.next
		return current_node

# 解析sgf属性
def sgf_prop(value_list):
	'Converts raw sgf library output to sensible value'
	if value_list is None:
		return None
	if len(value_list) == 1:
		return value_list[0]
	else:
		return value_list

# sgf的节点操作
# 节点操作是指A或者B下棋, play as B, or play as W.
def handle_node(panel, node):
	props = node.properties
	black_stones_added = [parse_sgf_coords(coords) for coords in props.get('AB', [])]
	white_stones_added = [parse_sgf_coords(coords) for coords in props.get('AW', [])]
	# 下子
	if black_stones_added or white_stones_added:
		return panel.add_stones(black_stones_added, white_stones_added)
	# If B/W props are not present, then there is no move. But if it is present and equal to the empty string, then the move was a pass.
	elif 'B' in props:
		black_move = parse_sgf_coords(props.get('B', [''])[0])
		return panel.addStone(black_move, color=go.blackChess)
	elif 'W' in props:
		white_move = parse_sgf_coords(props.get('W', [''])[0])
		return panel.addStone(white_move, color=go.whiteChess)
	else:
		return panel

# 将坐标转换
def parse_sgf_coords(s):
	'Interprets coords. aa is top left corner; sa is top right corner'
	if s is None or s == '':
		return None
	return SGF_COLUMNS.index(s[1]), SGF_COLUMNS.index(s[0])


if __name__ == "__main__":
	res = parse_sgf_coords('pp')
	print(res)

	res = parse_sgf_coords('dd')
	print(res)