import pygame
from queue import PriorityQueue
from colors import COLORS
from spot import Spot

pygame.init()
WIDTH_T, HEIGHT_T = 1000, 800
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH_T, HEIGHT_T))
pygame.display.set_caption("A* Path Finding Algorithm")
    
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return True
        
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()
    return False

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, COLORS['GREY'], (0, i*gap), (width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, COLORS['GREY'], (j*gap, 0), (j*gap, width))
    pygame.draw.line(win, COLORS['GREY'], (width, 0), (width, width))

def draw_info(win, text,x,y, size):
    font = pygame.font.Font(None, size)
    text = font.render(text, True, COLORS['BLACK'])
    win.blit(text,(x,y))

def draw_squares(win, color,x,y,w):
    pygame.draw.rect(win, color, pygame.Rect(x,y,w,w))


def draw(win, grid, rows, width):
    win.fill(COLORS['WHITE'])
    dist = 40
    for row in grid:
        for spot in row:
            spot.draw(win)
    draw_grid(win, rows, width)
    draw_info(win, 'A* Path finding', 820, 50, 30)
    draw_info(win, 'visualisation', 820, 70, 30)
    info_text = ['-Start', '-End', '-Barrier', '-Current', '-Checked', '-Final path']
    info_color = [COLORS['ORANGE'], COLORS['TURQUOISE'], COLORS['BLACK'], COLORS['GREEN'],
                  COLORS['RED'], COLORS['PURPLE']]
    for i in range(len(info_text)):
        draw_squares(win, info_color[i], 820, 100+dist*i, 30)
        draw_info(win, info_text[i], 860, 105+dist*i, 30)

    pygame.display.update()

def get_mouse_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row, col = y // gap, x // gap
    return row, col

def main(win, width):
    ROWS = 20
    grid = make_grid(ROWS, width)
    start, end = None, None
    run = True
    done = False
    border = False
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_mouse_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                elif spot != end and spot != start:
                    spot.make_barrier()
                    
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_mouse_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    if not done:
                        for row in grid:
                            for spot in row:
                                spot.update_neighbors(grid)
                        algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
                        done = True
                    else:
                        for row in grid:
                            for spot in row:
                                if spot.get_color() == COLORS['GREEN'] or spot.get_color() == COLORS['RED'] or spot.get_color() == COLORS['PURPLE']:
                                    spot.reset()
                        algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
                        done = False
                if event.key == pygame.K_r:
                    start, end = None, None
                    grid = make_grid(ROWS, width)
    pygame.quit()


if __name__ == "__main__":
    main(WIN, WIDTH)