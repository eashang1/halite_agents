from kaggle_environments.envs.halite.helpers import *
from random import choice


# Problems with current approach:
# If enemy ship is on halite (mining) and our ship has less halite,
# crash should occur with high priority

# Lists (some of) the objects

# board = Board(obs,config)
# board.cells
# board.ships
# board.shipyards
# board.players
# board.current_player
# board.current_player_id
# board.opponents
# board.configuration
# board.observation
# board.step
# board.next()
#
# cell.position
# cell.halite
# cell.ship
# cell.ship_id
# cell.shipyard
# cell.shipyard_id
# cell.north
# cell.south
# cell.east
# cell.west
#
# ship.id
# ship.halite
# ship.position
# ship.cell
# ship.player
# ship.player_id
# ship.next_action
#
# shipyard.id
# shipyard.position
# shipyard.cell
# shipyard.player
# shipyard.player_id
# shipyard.next_action
#
# player.id
# player.is_current_player
# player.halite
# player.next_actions
# player.ships
# player.ship_ids
# player.shipyards
# player.shipyard_ids

# Create position objects
class Position:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


# Calculates Manhattan distance
def manhattan_dist(p1, p2):
    dx = min(abs(p1.x - p2.x), 21 - abs(p1.x - p2.x))
    dy = min(abs(p1.y - p2.y), 21 - abs(p1.y - p2.y))
    return dx + dy


# Returns the distance to the nearest shipyard
def dist_shipyard(ship, shipyards):
    return min(map(lambda shipyard: manhattan_dist(ship.position, shipyard.position), shipyards), default=10000)


# Returns the closest shipyard
def closest_shipyard(ship, shipyards):
    return min(shipyards, key=lambda shipyard: manhattan_dist(ship.position, shipyard.position))


# Moves a ship to deposit to the nearest shipyard
def deposit(ship, shipyards):
    east = Position((ship.position.x + 1) % 21, ship.position.y)
    west = Position((ship.position.x - 1) % 21, ship.position.y)
    north = Position(ship.position.x, (ship.position.y + 1) % 21)
    south = Position(ship.position.x, (ship.position.y - 1) % 21)

    shipyard = closest_shipyard(ship, shipyards)
    best = min([east, west, north, south], key=lambda new_position: manhattan_dist(new_position, shipyard.position))

    if east is best:
        ship.next_action = ShipAction.EAST
    elif west is best:
        ship.next_action = ShipAction.WEST
    elif north is best:
        ship.next_action = ShipAction.NORTH
    elif south is best:
        ship.next_action = ShipAction.SOUTH


# Moves a ship towards a specified position
def move_towards(ship, target):
    east = Position((ship.position.x + 1) % 21, ship.position.y)
    west = Position((ship.position.x - 1) % 21, ship.position.y)
    north = Position(ship.position.x, (ship.position.y + 1) % 21)
    south = Position(ship.position.x, (ship.position.y - 1) % 21)

    best = min([east, west, north, south], key=lambda d: manhattan_dist(d, target))

    if east is best:
        ship.next_action = ShipAction.EAST
    elif west is best:
        ship.next_action = ShipAction.WEST
    elif north is best:
        ship.next_action = ShipAction.NORTH
    elif south is best:
        ship.next_action = ShipAction.SOUTH


# Moves a ship away from the nearest shipyard
def move_away(ship, shipyards):
    if dist_shipyard(ship, shipyards) == 0:
        ship.next_action = choice([ShipAction.NORTH, ShipAction.EAST, ShipAction.SOUTH, ShipAction.WEST])
    else:
        deposit(ship, shipyards)
        if ship.next_action is ShipAction.EAST:
            ship.next_action = ShipAction.WEST
        elif ship.next_action is ShipAction.WEST:
            ship.next_action = ShipAction.EAST
        elif ship.next_action is ShipAction.NORTH:
            ship.next_action = ShipAction.SOUTH
        elif ship.next_action is ShipAction.SOUTH:
            ship.next_action = ShipAction.NORTH


# Returns true if there is a nearby ship on the next turn
def nearby_ships(shipyard, ships):
    for ship in ships:
        if shipyard.position == next_pos(ship):
            return True
    return False


# Checks if a ship is crashing
def crash(ship, ships):
    new_pos = next_pos(ship)
    for other in ships:
        if other is ship:
            continue
        check = next_pos(other)
        if new_pos == check:
            return True
    return False


# Returns the next position of a ship given it's next action
def next_pos(ship):
    if ship.next_action is ShipAction.NORTH:
        return Position(ship.position.x, (ship.position.y + 1) % 21)
    elif ship.next_action is ShipAction.SOUTH:
        return Position(ship.position.x, (ship.position.y - 1) % 21)
    elif ship.next_action is ShipAction.EAST:
        return Position((ship.position.x + 1) % 21, ship.position.y)
    elif ship.next_action is ShipAction.WEST:
        return Position((ship.position.x - 1) % 21, ship.position.y)
    else:
        return ship.position


# Avoids crashes
def avoid_crash(ship, ships):
    if ship.next_action is None:
        return

    if crash(ship, ships):
        ship.next_action = ShipAction.NORTH
    if crash(ship, ships):
        ship.next_action = ShipAction.SOUTH
    if crash(ship, ships):
        ship.next_action = ShipAction.EAST
    if crash(ship, ships):
        ship.next_action = ShipAction.WEST
    if crash(ship, ships):
        ship.next_action = None


# move towards halite or nearby enemy base
def find_move(ship, free, enemy_bases):
    best_base = min(enemy_bases, key=lambda target: manhattan_dist(target, ship.position), default=None)
    best_halite = min(free, key=lambda target: manhattan_dist(target, ship.position), default=None)

    if best_base is not None and ship.halite < 200 and manhattan_dist(best_base, ship.position) < 4:
        move_towards(ship, best_base)
        enemy_bases.remove(best_base)
    elif best_halite is not None:
        move_towards(ship, best_halite)
        free.remove(best_halite)
    else:
        ship.next_action = choice([ShipAction.NORTH, ShipAction.EAST, ShipAction.SOUTH, ShipAction.WEST])


def agent(obs, config):
    # Note that this board is a torus
    board = Board(obs, config)
    me = board.current_player

    cost = 0
    free = set()
    for x in range(21):
        for y in range(21):
            if (board.cells[Point(x, y)].halite >= 120 and not any(
                    map(lambda s: s.position == Point(x, y), me.ships))):
                free.add(Point(x, y))

    enemy_bases = {s.position for opponent in board.opponents for s in opponent.shipyards}
    enemy_ships = {s for opponent in board.opponents for s in opponent.ships}

    # Set actions for each ship
    for ship in me.ships:
        ship.next_action = None

        # destroys passing enemy ships
        done = False
        for bad in enemy_ships:
            if manhattan_dist(ship.position, bad.position) == 1 and ship.halite < bad.halite and \
                    board.cells[bad.position].halite >= 120:
                move_towards(ship, bad.position)
                done = True
                break
        if done:
            continue

        if (len(me.shipyards) == 0 and me.halite - cost >= 500) or \
                (
                        me.halite - cost >= 800 and
                        board.step <= 310 and
                        dist_shipyard(ship, me.shipyards) > 7 and
                        ship.halite < 200):
            # if no shipyards or Manhattan distance of at least 7, make a shipyard
            ship.next_action = ShipAction.CONVERT
            cost += 500
        elif board.cells[ship.position].halite >= 120:
            # if on halite, mine it
            ship.next_action = None
        elif (ship.halite >= 300 or (ship.halite >= 75 and board.step >= 345)) and len(me.shipyards):
            # if halite > 1000, move to deposit
            deposit(ship, me.shipyards)
        else:
            # moves towards a nearby target
            find_move(ship, free, enemy_bases)

    # Set actions for each shipyard
    for shipyard in me.shipyards:
        shipyard.next_action = None
        if ((len(me.ships) == 0 and me.halite - cost >= 500) or
            (me.halite - cost >= 500 and board.step <= 335)) and not nearby_ships(shipyard, me.ships):
            # if we have no ships or a lot of halite and many turns left make more while you can
            shipyard.next_action = ShipyardAction.SPAWN
            cost += 500

    for ship in me.ships:
        avoid_crash(ship, me.ships)

    return me.next_actions
