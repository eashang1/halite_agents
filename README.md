# Halite
Includes agents for Halite entered into the "Halite by Two-Sigma - Playground Edition" Kaggle contest 

Halite is a turn based resource management game in which players control and grow a fleet of ships. For more detailed rules, see: https://www.kaggle.com/c/halite

naive_implementation.py: Our intial approach with random movement and hard coded rules to prevent events such as crashes

heuristic.py: Our best performing agent that used various heuristics to move ships towards halite-rich cells and enemy bases

monte_carlo.py: An unfinished MCTS approach (which combines techniques from both naive_implementation.py and heuristic.py) that I intend to complete and submit for the Halite Season V Kaggle contest

To see our agent play, see: https://www.kaggle.com/c/halite-iv-playground-edition/leaderboard?dialog=episodes-submission-18810444
