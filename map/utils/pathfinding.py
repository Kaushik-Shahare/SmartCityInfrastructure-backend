import heapq
from map.models import MatrixMap, Point

def get_road_set(matrix):
    # Build a set of (x, y) for points that represent 'road'
    qs = matrix.points.filter(represents='road')
    road_set = {(p.x, p.y) for p in qs}
    return road_set

def in_bounds(point, matrix):
    x, y = point
    return 0 <= x < matrix.X and 0 <= y < matrix.Y

def neighbors(point, road_set, matrix):
    x, y = point
    nbrs = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
    return [p for p in nbrs if in_bounds(p, matrix) and p in road_set]

def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

def dijkstra(matrix, start, end, explored_nodes=None):
    road_set = get_road_set(matrix)
    
    
    if start not in road_set or end not in road_set:
        print(f"DEBUG: Dijkstra - Start or end point is not a road")
        return None
    
    dist = {start: 0}
    came_from = {}
    heap = [(0, start)]
    visited = set()
    
    if explored_nodes is not None:  # If we're tracking explored nodes for viz
        explored_nodes.append(start)
    
    while heap:
        current_dist, current = heapq.heappop(heap)
        
        if current in visited:
            continue
            
        visited.add(current)
        
        if current == end:
            path = reconstruct_path(came_from, current)
            return path
        
        nbrs = neighbors(current, road_set, matrix)
        
        for nbr in nbrs:
            if nbr in visited:
                continue
                
            alt = current_dist + 1  # uniform cost
            
            if explored_nodes is not None:  # Track explored nodes
                explored_nodes.append(nbr)
                
            if alt < dist.get(nbr, float('inf')):
                dist[nbr] = alt
                came_from[nbr] = current
                heapq.heappush(heap, (alt, nbr))
    
    return None

def a_star(matrix, start, end, explored_nodes=None):
    road_set = get_road_set(matrix)
    
    
    if start not in road_set or end not in road_set:
        return None
    
    open_set = []
    heapq.heappush(open_set, (manhattan(start, end), 0, start))
    came_from = {}
    g_score = {start: 0}
    visited = set()
    
    if explored_nodes is not None:
        explored_nodes.append(start)
    
    while open_set:
        _, current_g, current = heapq.heappop(open_set)
        
        if current in visited:
            continue
            
        visited.add(current)
        
        if current == end:
            path = reconstruct_path(came_from, current)
            return path
        
        nbrs = neighbors(current, road_set, matrix)
        
        for nbr in nbrs:
            if nbr in visited:
                continue
                
            tentative = g_score[current] + 1
            
            if explored_nodes is not None:
                explored_nodes.append(nbr)
                
            if tentative < g_score.get(nbr, float('inf')):
                came_from[nbr] = current
                g_score[nbr] = tentative
                f_score = tentative + manhattan(nbr, end)
                heapq.heappush(open_set, (f_score, tentative, nbr))
    
    return None

def find_next_closest_road(matrix, start, target, algorithm='dijkstra', explored_nodes=None):
    road_set = get_road_set(matrix)
    best = None
    best_path = None
    for pt in road_set:
        if pt == target:
            continue
        path = dijkstra(matrix, start, pt, explored_nodes) if algorithm == 'dijkstra' else a_star(matrix, start, pt, explored_nodes)
        if path:
            d = manhattan(pt, target)
            if best is None or d < best:
                best = d
                best_path = path
    return best_path
