import pygame
import sys
from aima.search import Problem, astar_search

# Hằng số
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 736
TILE_SIZE = 32

# Lớp vấn đề ma trận
class GridProblem(Problem):
    def __init__(self, matrix, start, goal):
        super().__init__(start, goal)  # Khởi tạo lớp cha với trạng thái bắt đầu và kết thúc
        self.matrix = matrix  # Ma trận mô tả bản đồ
        self.width = len(matrix[0])  # Chiều rộng của ma trận
        self.height = len(matrix)  # Chiều cao của ma trận

    def actions(self, state):
        x, y = state  # Lấy tọa độ hiện tại
        actions = []  # Danh sách hành động khả thi
        # Duyệt qua các hướng di chuyển (trên, dưới, trái, phải)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy  # Tính tọa độ mới
            # Kiểm tra xem tọa độ mới có hợp lệ và không phải vật cản không
            if 0 <= nx < self.width and 0 <= ny < self.height and self.matrix[ny][nx] == 1:
                actions.append((nx, ny))  # Thêm hành động vào danh sách
        return actions

    def result(self, state, action):
        return action  # Trả về hành động kết quả từ trạng thái hiện tại

    def goal_test(self, state):
        return state == self.goal  # Kiểm tra xem trạng thái hiện tại có phải là trạng thái mục tiêu không

    def path_cost(self, cost, state1, action, state2):
        return cost + 1  # Tính chi phí đi từ trạng thái này sang trạng thái khác (luôn là 1)

    def h(self, node):
        state = node.state  # Lấy trạng thái của node
        goal_x, goal_y = self.goal  # Tọa độ mục tiêu
        state_x, state_y = state  # Tọa độ hiện tại
        # Tính khoảng cách Manhattan giữa trạng thái hiện tại và mục tiêu
        return abs(goal_x - state_x) + abs(goal_y - state_y)

# Lớp Roomba
class Roomba(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()  # Khởi tạo lớp cha
        self.image = pygame.image.load('roomba.png').convert_alpha()  # Tải hình ảnh Roomba
        self.rect = self.image.get_rect(center=(60, 60))  # Tạo hình chữ nhật cho Roomba
        self.pos = self.rect.center  # Vị trí hiện tại của Roomba
        self.speed = 7  # Tốc độ di chuyển
        self.direction = pygame.math.Vector2(0, 0)  # Hướng di chuyển
        self.path = []  # Đường đi

    def get_coord(self):
        col = self.rect.centerx // TILE_SIZE  # Tính cột
        row = self.rect.centery // TILE_SIZE  # Tính hàng
        return (col, row)  # Trả về tọa độ

    def set_path(self, path):
        self.path = path  # Gán đường đi
        self.get_direction()  # Cập nhật hướng di chuyển

    def get_direction(self):
        if self.path:
            start = pygame.math.Vector2(self.pos)  # Vị trí bắt đầu
            end = pygame.math.Vector2(self.path[0][0] * TILE_SIZE + TILE_SIZE // 2,
                                        self.path[0][1] * TILE_SIZE + TILE_SIZE // 2)  # Tính vị trí kết thúc
            self.direction = (end - start).normalize()  # Cập nhật hướng di chuyển
        else:
            self.direction = pygame.math.Vector2(0, 0)  # Không có đường đi
            self.path = []  # Đặt lại đường đi

    def update(self):
        self.pos += self.direction * self.speed  # Cập nhật vị trí
        # Kiểm tra xem Roomba có đạt đến điểm đầu tiên trong đường đi không
        if self.path and self.rect.collidepoint(self.path[0][0] * TILE_SIZE + TILE_SIZE // 2,
                                                 self.path[0][1] * TILE_SIZE + TILE_SIZE // 2):
            self.path.pop(0)  # Xóa điểm đã đạt đến
            self.get_direction()  # Cập nhật hướng di chuyển
        self.rect.center = self.pos  # Cập nhật vị trí hình chữ nhật

# Lớp tìm đường
class Pathfinder:
    def __init__(self, matrix):
        self.matrix = matrix  # Lưu ma trận
        self.roomba = pygame.sprite.GroupSingle(Roomba())  # Tạo đối tượng Roomba
        self.path = []  # Đường đi
        self.goal_image = None  # Lưu vị trí hình ảnh mục tiêu
        self.hovered_tile = None  # Lưu vị trí ô được hover

    def create_path(self, start, goal):
        self.roomba.sprite.set_path([])  # Xóa đường đi hiện tại
        # Kiểm tra vị trí bắt đầu
        if not (0 <= start[0] < len(self.matrix[0])) or not (0 <= start[1] < len(self.matrix)):
            print(f"Vị trí bắt đầu không hợp lệ: {start}")  # Xuất thông báo
            return
        
        # Kiểm tra vị trí mục tiêu
        if not (0 <= goal[0] < len(self.matrix[0])) or not (0 <= goal[1] < len(self.matrix)):
            print(f"Vị trí mục tiêu không hợp lệ: {goal}")  # Xuất thông báo
            return
        
        problem = GridProblem(self.matrix, start, goal)  # Tạo đối tượng vấn đề
        solution = astar_search(problem)  # Tìm kiếm đường đi
        if solution:
            self.path = [(node.state[0], node.state[1]) for node in solution.path()]  # Lưu đường đi
            print(f"Đường đi đã tìm thấy: {self.path}")  # Xuất thông báo
            self.roomba.sprite.set_path(self.path)  # Cập nhật đường đi cho Roomba
            self.goal_image = goal  # Lưu vị trí mục tiêu
        else:
            print("Không tìm thấy đường đi!")  # Xuất thông báo

    def update_hovered_tile(self, mouse_pos):
        # Chuyển đổi vị trí chuột thành tọa độ ô
        hovered_coord = (mouse_pos[0] // TILE_SIZE, mouse_pos[1] // TILE_SIZE)
        # Kiểm tra ô được hover có hợp lệ không
        if (0 <= hovered_coord[0] < len(self.matrix[0]) and 
            0 <= hovered_coord[1] < len(self.matrix) and 
            self.matrix[hovered_coord[1]][hovered_coord[0]] == 1):
            self.hovered_tile = hovered_coord  # Lưu ô hợp lệ
        else:
            self.hovered_tile = None  # Xóa nếu là vật cản hoặc ra ngoài giới hạn

    def draw_path(self, screen):
        # Vẽ đường đi nếu có ít nhất 2 điểm
        if len(self.path) >= 2:
            points = [(point[0] * TILE_SIZE + TILE_SIZE // 2, point[1] * TILE_SIZE + TILE_SIZE // 2) for point in self.path]
            pygame.draw.lines(screen, '#4a4a4a', False, points, 5)  # Vẽ đường đi

    def update(self, screen):
        self.roomba.update()  # Cập nhật vị trí của Roomba
        self.roomba.draw(screen)  # Vẽ Roomba

        # Kiểm tra xem Roomba có đạt đến mục tiêu không
        if self.roomba.sprite.get_coord() == self.goal_image:
            self.goal_image = None  # Xóa hình ảnh mục tiêu khi đạt đến
        
        if self.goal_image:
            # Vẽ hình ảnh tại vị trí mục tiêu
            goal_x, goal_y = self.goal_image
            goal_rect = pygame.Rect(goal_x * TILE_SIZE, goal_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            goal_surf = pygame.image.load('selection.png').convert_alpha()
            screen.blit(goal_surf, goal_rect)

        # Vẽ hình ảnh tại vị trí được hover nếu hợp lệ
        if self.hovered_tile:
            hover_x, hover_y = self.hovered_tile
            hover_rect = pygame.Rect(hover_x * TILE_SIZE, hover_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            hover_surf = pygame.image.load('selection.png').convert_alpha()
            screen.blit(hover_surf, hover_rect)

# Khởi tạo trò chơi
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
bg_surf = pygame.image.load('map.png').convert()
matrix = [
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
	[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
	[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
	[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,0,0,1,1,1,1,1,0,0,0,0,1,1,1,1,0],
	[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,0,0,1,1,1,1,1,0,0,0,0,1,1,1,1,0],
	[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,0,0,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
	[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,0,0,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
	[0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,1,1,0,0,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,1,1,0,0,1,0,0,1,1,1,1,0,0,0,0,0,0,1,1,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,0,0,0,0,0,0,1,1,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0],
	[0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0],
	[0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
	[0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
	[0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0],
	[0,1,1,1,1,1,1,1,1,0,0,0,0,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,1,1,1,0,0,0],
	[0,1,1,1,1,1,0,0,1,0,0,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,0,0,1,1,1,1,0,0,0],
	[0,0,0,1,1,1,0,0,1,1,1,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,0],
	[0,0,0,1,1,1,1,1,1,1,1,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,0],
	[0,1,1,1,1,1,1,1,1,0,0,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,0,0,1,1,0],
	[0,1,1,1,1,1,1,1,1,0,0,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,0,0,1,1,0],
	[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

# Vòng lặp chính của trò chơi
pathfinder = Pathfinder(matrix)  # Khởi tạo đối tượng tìm đường
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Khi nhấn chuột, lấy tọa độ ô và tạo đường đi từ Roomba đến ô đó
            start = pathfinder.roomba.sprite.get_coord()  # Lấy tọa độ hiện tại của Roomba
            pathfinder.create_path(start, (event.pos[0] // TILE_SIZE, event.pos[1] // TILE_SIZE))

    # Cập nhật hình nền và vẽ các phần tử
    screen.blit(bg_surf, (0, 0))
    pathfinder.update_hovered_tile(pygame.mouse.get_pos())  # Cập nhật ô được hover
    pathfinder.draw_path(screen)  # Vẽ đường đi
    pathfinder.update(screen)  # Cập nhật và vẽ Roomba
    pygame.display.flip()  # Cập nhật màn hình
    clock.tick(60)  # Giới hạn FPS

pygame.quit()  # Thoát trò chơi
sys.exit()
