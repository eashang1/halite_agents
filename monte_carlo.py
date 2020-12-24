from kaggle_environments.envs.halite.helpers import *
import random
import numpy as np


# Problems with current approach:
# doesn't work

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

# Ensures a list of actions is valid (no crashes, sufficient halite, etc.)
def make_valid(actions):
    pass


# Returns a number representing how good a list of moves is
def heuristic(actions):
    pass


def agent(obs, config):
    # Note that this board is a torus
    board = Board(obs, config)
    me = board.current_player

    # Set actions for each ship
    best = list()
    ship_actions = [ShipAction.NORTH, ShipAction.SOUTH, ShipAction.EAST, ShipAction.WEST, ShipAction.CONVERT, None]
    shipyard_actions = [ShipyardAction.SPAWN, None]

    for i in range(1, 1000):
        current = list()

        for ship in me.ships:
            current.append(random.choice(ship_actions))

        make_valid(current)

        if heuristic(current) > heuristic(best):
            best = current

            j = 0
            for ship in me.ships:
                ship.next_action = current[j]
                j += 1

    return me.next_actions
