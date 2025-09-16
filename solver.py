import random
import matplotlib.pyplot as plt
from collections import Counter


def roll_fresh():
    """
    Perform a 'fresh' 2d6 roll.
    If (3,1) appears, discard and re-roll.
    """
    while True:
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        if not (d1 == 3 and d2 == 1):
            return (d1, d2)

def roll_locked():
    """
    Perform a 'locked' throw: one die is forced to be 3.
    """
    d_free = random.randint(1, 6)
    if d_free == 1:
        return roll_fresh()
    else:
        return (3, d_free)

def is_double(d1, d2):
    return d1 == d2

def is_snake_eyes(d1, d2):
    return d1 == 1 and d2 == 1

def contains_3(d1, d2):
    return 3 in (d1, d2)

def shots_for_double(d1, d2):
    """
    For a double, return the face value (e.g., (4,4) gives 4).
    """
    if d1 == d2:
        return d1
    return 0

def simulate_initial_turn(candidate):
    """
    Simulate a single candidate's turn (3 throws with locked-dice rules)
    for the purpose of becoming HM.
    """
    # Throw 1 (always fresh)
    d1, d2 = roll_fresh()
    if is_double(d1, d2) and (d1, d2) == (1,1):
        return True, 1
    # Decide if throw 2 is locked:
    T2_locked = contains_3(d1, d2)
    if T2_locked:
        d1_2, d2_2 = roll_locked()
    else:
        d1_2, d2_2 = roll_fresh()
    if is_double(d1_2, d2_2) and (d1_2, d2_2) == (1,1):
        return True, 2
    # Throw 3: locked if T2 was fresh and had a 3; if T2 was locked, then throw 3 is fresh.
    if T2_locked:
        T3_locked = False
    else:
        T3_locked = contains_3(d1_2, d2_2)
    if T3_locked:
        d1_3, d2_3 = roll_locked()
    else:
        d1_3, d2_3 = roll_fresh()
    if is_double(d1_3, d2_3) and (d1_3, d2_3) == (1,1):
        return True, 3
    return False, None

def run_single_simulation(num_players=5):
    """
    Run one simulation:
      1. Cycle through candidate turns until one becomes HM by rolling (1,1)
      2. Once HM is established, start with the player immediately after HM.
         For each subsequent turn (3 throws per turn using locked rules):
           - If the current player is HM:
                 any hundred–result (double) adds its face value to givenShots.
           - If the current player is not HM:
                 if a hundred–result occurs:
                     • if it is (1,1), then that roll (which would dethrone HM)
                       stops the simulation (and we do not add any shot for this roll);
                     • otherwise, add its face value to receivedShots.
         The simulation stops as soon as a non–HM throws (1,1).
    """
    # --- Phase 1: Determine HM ---
    candidate = 0
    hm_found = False
    hm_id = None
    while not hm_found:
        becameHM, throw_num = simulate_initial_turn(candidate)
        if becameHM:
            hm_found = True
            hm_id = candidate
            # (Optionally, you could record throw_num to know on which throw HM was achieved.)
            break
        candidate = (candidate + 1) % num_players

    # --- Phase 2: HM Torture ---
    receivedShots = 0
    givenShots = 0
    # Start with the player immediately after HM.
    current_player = (hm_id + 1) % num_players
    dethroned = False

    while not dethroned:
        # Each player's turn consists of up to 3 throws.
        # Throw 1: always fresh.
        d1, d2 = roll_fresh()
        if is_double(d1, d2):
            if current_player == hm_id:
                givenShots += shots_for_double(d1, d2)
            else:
                # For a non-HM, if (1,1) is rolled then HM is dethroned.
                if (d1, d2) == (1,1):
                    dethroned = True
                    # Do not add shot for the dethronement roll.
                    break
                else:
                    receivedShots += shots_for_double(d1, d2)
        # Decide on throw 2:
        T2_locked = contains_3(d1, d2)
        if T2_locked:
            d1_2, d2_2 = roll_locked()
        else:
            d1_2, d2_2 = roll_fresh()
        if is_double(d1_2, d2_2):
            if current_player == hm_id:
                givenShots += shots_for_double(d1_2, d2_2)
            else:
                if (d1_2, d2_2) == (1,1):
                    dethroned = True
                    break
                else:
                    receivedShots += shots_for_double(d1_2, d2_2)
        # Decide on throw 3:
        if T2_locked:
            T3_locked = False
        else:
            T3_locked = contains_3(d1_2, d2_2)
        if T3_locked:
            d1_3, d2_3 = roll_locked()
        else:
            d1_3, d2_3 = roll_fresh()
        if is_double(d1_3, d2_3):
            if current_player == hm_id:
                givenShots += shots_for_double(d1_3, d2_3)
            else:
                if (d1_3, d2_3) == (1,1):
                    dethroned = True
                    break
                else:
                    receivedShots += shots_for_double(d1_3, d2_3)
        # End of current player's turn; move to next player.
        current_player = (current_player + 1) % num_players

    return hm_id, receivedShots, givenShots

def run_monte_carlo_simulations(num_sims=5000, num_players=5):
    """
    Run many simulations.
    Returns lists of hm_ids, receivedShots, and givenShots.
    """
    hm_ids = []
    received_list = []
    given_list = []
    for _ in range(num_sims):
        hm_id, rec, giv = run_single_simulation(num_players)
        hm_ids.append(hm_id)
        received_list.append(rec)
        given_list.append(giv)
    return hm_ids, received_list, given_list

def main():
    random.seed(42)
    NUM_SIMS = 5000
    NUM_PLAYERS = 5

    hm_ids, rec_shots, giv_shots = run_monte_carlo_simulations(NUM_SIMS, NUM_PLAYERS)
    
    avg_received = sum(rec_shots) / len(rec_shots)
    avg_given = sum(giv_shots) / len(giv_shots)
    print("After {} simulations with {} players:".format(NUM_SIMS, NUM_PLAYERS))
    print("  Average receivedShots (from non-HM turns): {:.3f}".format(avg_received))
    print("  Average givenShots (from HM turns): {:.3f}".format(avg_given))
    

    rec_counts = Counter(rec_shots)
    giv_counts = Counter(giv_shots)

    fig, ax = plt.subplots(1, 2, figsize=(14,6))
    ax[0].bar(rec_counts.keys(), rec_counts.values(), color='green', alpha=0.7)
    ax[0].set_title("Distribution of Received Shots")
    ax[0].set_xlabel("Received Shots")
    ax[0].set_ylabel("Frequency")

    ax[1].bar(giv_counts.keys(), giv_counts.values(), color='red', alpha=0.7)
    ax[1].set_title("Distribution of Given Shots (HM)")
    ax[1].set_xlabel("Given Shots")
    ax[1].set_ylabel("Frequency")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
