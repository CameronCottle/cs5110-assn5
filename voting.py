import random
import numpy

CAND = 0  # subscript of list which represents the candidate
SCORE = 1  # subscript of list which represents the score of the candidate
PLACE = 2  # subscript of list which represents the ranking, lowest is best

def print_connections(names, c, voters, candidates):
    print("CONNECTIONS")
    for i in range(voters):
        print("%10s" % (names[i]), end=" ")
        for j in range(voters):
            print(c[i][j], end=' ')
        print()


def print_rankings(names, r, voters, candidates, ordered):
    print("CANDIDATE Rankings")
    for i in range(voters):
        #print("First choice for {} is {}".format(names[i], ordered[i][CAND]), end=" ")
        print(names[i], end=" ")
        for j in range(candidates):
            print(r[i][j], end='')
        print(" ORDER ", ordered[i])


def create_voting(voters, candidates):
    names = ["Alice ", "Bart  ", "Cindy ", "Darin ", "Elmer ", "Finn  ", "Greg  ", "Hank  ", "Ian   ", "Jim   ",
             "Kate  ", "Linc  ", "Mary  ", "Nancy ", "Owen  ", "Peter ", "Quinn ", "Ross  ", "Sandy ", "Tom   ",
             "Ursula", "Van   ", "Wendy ", "Xavier", "Yan   ", "Zach  "]

    connections = [[0 for i in range(voters)] for j in range(voters)]
    ordered = [[] for i in range(voters)]
    numpy.random.seed(1052)
    for i in range(voters):
        conn = round(numpy.random.uniform(0, voters / 2))
        for j in range(conn):
            connectTo = numpy.random.randint(0, voters)
            if (connectTo!=i):
                connections[i][connectTo] = 1
    print_connections(names, connections, voters, candidates)
    candidateRanking = [[list() for i in range(candidates)] for j in range(voters)]
    for i in range(voters):
        for j in range(candidates):
            candidateRanking[i][j] = [j + 1, round(numpy.random.uniform(0, 100)) / 10, 0]
        # print(candidateRanking[i])
        s = sorted(candidateRanking[i], reverse=True, key=lambda v: v[SCORE])
        ordered[i] = [s[i][CAND] for i in range(candidates)]
        for v in range(candidates):
            candidate = s[v][CAND] - 1  # which candidate has rank v+1
            candidateRanking[i][candidate][PLACE] = v + 1
    print_rankings(names, candidateRanking, voters, candidates, ordered)
    return names, candidateRanking, ordered, connections

def ranked_choice_winner(orderRankings):
    # find the number of candidates
    numCandidates = 0
    for b in orderRankings:
        for c in b:
            if c > numCandidates:
                numCandidates = c
    candidates = set(range(1, numCandidates + 1))
    eliminationOrder = []
    roundNumber = 1

    print("\n---RANKED CHOICE VOTING---")
    while True:
        print(f"\nROUND {roundNumber}")
        roundNumber += 1
        # count first preference for each ballot
        counts = {cid: 0 for cid in candidates}
        for b in orderRankings:
            for choice in b:
                if choice in candidates:
                    counts[choice] += 1
                    break

        totalCandidatesVotes = sum(counts.values())

        # check for majority (winner)
        for candidate, votes in counts.items():
            if votes > totalCandidatesVotes / 2:
                print(f"Candidate {candidate} wins with {votes} votes")
                print("\nElimination order:", eliminationOrder)
                return candidate, eliminationOrder

        # if no candidates votes, stop
        if totalCandidatesVotes == 0:
            print("All rankings exhausted. No winner.")
            return None, eliminationOrder

        # find the candidate with the least amount of votes
        minVotes = min(counts.values())
        toEliminate = [candidate for candidate, votes in counts.items() if votes == minVotes]

        # break the tie by eliminating the one(s) with the most last-choice votes.
        if len(toEliminate) > 1:
            # count last-place preferences among currently active candidates
            lastCounts = {candidate: 0 for candidate in candidates}
            for b in orderRankings:
                # find the last-ranked active candidate on this ballot
                for choice in reversed(b):
                    if choice in candidates:
                        lastCounts[choice] += 1
                        break

            # look only at the tied candidates
            tiedLast = {candidate: lastCounts[candidate] for candidate in toEliminate}
            maxLast = max(tiedLast.values())
            # candidates among the tied with the maximum last-place votes
            toEliminateByLast = [candidate for candidate, lc in tiedLast.items() if lc == maxLast]

            # if this narrows the set, use it; otherwise keep eliminating all tied
            if len(toEliminateByLast) > 0 and len(toEliminateByLast) < len(toEliminate):
                toEliminate = toEliminateByLast
        print("Eliminating candidates:", toEliminate)
        for candidate in toEliminate:
            candidates.remove(candidate)
            eliminationOrder.append(candidate)

def cardinal_social_welfare(winner, rankings):
    numVoters = len(rankings)

    total = 0.0
    for i in range(numVoters):
        ballot = rankings[i]
        scores = [entry[SCORE] for entry in ballot]
        best = max(scores)
        winnerScore = ballot[winner - 1][SCORE]

        utility = best - winnerScore
        total += utility

    print(f"Total cardinal social welfare when candidate {winner} wins: {total:.3f}")
    return total

# calculate ordinal score for 
def ordinal_social_welfare(winner, orderedRankings):
    total = 0
    for i, order in enumerate(orderedRankings):
        place = order.index(winner) + 1
        util = place - 1
        total += util
    print(f"Total ordinal social welfare when candidate {winner} wins: {total}")
    return total

def ordinal_social_welfare_actual(winner, candidateRanking):
    numVoters = len(candidateRanking)
    total = 0
    for i in range(numVoters):
        place = candidateRanking[i][winner - 1][PLACE]
        util = place - 1
        total += util
    print(f"Total ordinal social welfare when candidate {winner} wins: {total}")
    return total

def defensive_voting(connections, ordered, candidateRanking, threshold=0.3, maxRounds=10, seed=None):
    numVoters = len(ordered)
    numCandidates = len(ordered[0])

    votes = [ordered[i][0] for i in range(numVoters)]
    changesPerRound = []
    randomSeed = random.Random(seed)

    for _ in range(1, maxRounds + 1):
        changes = 0
        indices = list(range(numVoters))
        randomSeed.shuffle(indices)

        # process each voter in random order and look at their neighbors rankings
        for i in indices:
            neighbor = [j for j, val in enumerate(connections[i]) if val]
            deg = len(neighbor)
            if deg == 0:
                continue

            # find voter's last choice candidate
            lastChoice = None
            for entry in candidateRanking[i]:
                if entry[PLACE] == numCandidates:
                    lastChoice = entry[CAND]
                    break

            countLast = sum(1 for j in neighbor if votes[j] == lastChoice)
            if countLast / deg > threshold:
                neighborCounts = {}
                for j in neighbor:
                    c = votes[j]
                    if c == lastChoice:
                        continue
                    neighborCounts[c] = neighborCounts.get(c, 0) + 1

                newVote = votes[i]
                if neighborCounts:
                    maxCount = max(neighborCounts.values())
                    candidatesMax = [c for c, cnt in neighborCounts.items() if cnt == maxCount]
                    bestC = min(candidatesMax, key=lambda c: candidateRanking[i][c - 1][PLACE])
                    newVote = bestC
                else:
                    if len(ordered[i]) >= 2:
                        newVote = ordered[i][1]

                if newVote != votes[i]:
                    votes[i] = newVote
                    changes += 1

        changesPerRound.append(changes)
        if changes == 0:
            break

    finalCounts = {}
    for v in votes:
        finalCounts[v] = finalCounts.get(v, 0) + 1
    finalWinner = max(finalCounts.items(), key=lambda kv: kv[1])[0] if finalCounts else None
    return finalWinner, changesPerRound, votes

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    NUM_VOTERS = 20
    NUM_CANDIDATES = 5

    names, rankings, orderRanking, connections = create_voting(NUM_VOTERS, NUM_CANDIDATES)

    print("\n--- PART 1: RANKED CHOICE VOTING ---")
    winner, eliminationOrder = ranked_choice_winner(orderRanking)
    print("\nElimination order:", eliminationOrder)
    print("Ranked-choice winner:", winner)

    # social welfare for ranked-choice winner
    cardinal_social_welfare(winner, rankings)
    ordinal_social_welfare(winner, orderRanking)

    # ----- PART 2 -----
    print("\n--- PART 2: SOCIAL NETWORK SIMULATION (Defensive Voting Strategy) ---")

    winner2, changesPerRound, finalVotes = defensive_voting(connections, orderRanking, rankings, threshold=0.2, maxRounds=10, seed=42)

    print(f"\nSocial network winner: {winner2}")
    for r, c in enumerate(changesPerRound, start=1):
        print(f"Round {r}: {c} voters changed their vote")

    # social welfare based on true preferences
    cardinal_social_welfare(winner2, rankings)
    ordinal_social_welfare_actual(winner2, rankings)




