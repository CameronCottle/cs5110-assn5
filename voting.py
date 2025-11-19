
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
    return names, candidateRanking, ordered

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

def cardinal_social_welfare(names, winner, rankings):
    numVoters = len(rankings)
    numCandidates = len(rankings[0])

    # for each possible winner, compute each voter's cardinal utility (winner score - last score)
    print(f"\nCardinal social welfare if {winner} wins:")
    total = 0.0
    for i in range(numVoters):
        ballot = rankings[i]
        winnerScore = ballot[winner - 1][SCORE]
        lastScore = None
        for entry in ballot:
            if entry[PLACE] == numCandidates:
                lastScore = entry[SCORE]
                break
        if lastScore is None:
            lastScore = min(e[SCORE] for e in ballot)

        utility = winnerScore - lastScore
        total += utility
        print(f"- {names[i]}: {utility:.3f}")
    print(f"Total cardinal social welfare if {winner} wins: {total:.3f}")

def ordinal_social_welfare(names, orderedRankings, winner=None):
    numCandidates = len(orderedRankings[0])
    print(f"\nOrdinal utilities with candidate {winner} winning:")
    total = 0
    for i, b in enumerate(orderedRankings):
        # find position of winner in this ballot
        pos = b.index(winner)
        winnerPoints = numCandidates - pos

        # last place points is always 1 
        lastPoints = 1
        
        utility = winnerPoints - lastPoints
        total += utility
        voterName = names[i] if names is not None else i
        print(f"- {voterName}: {utility}")

    print(f"Total ordinal social welfare if {winner} wins: {total}")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    names, rankings, orderRanking = create_voting(20, 5)
    winner, eliminationOrder = ranked_choice_winner(orderRanking)
    print("\nElimination order:", eliminationOrder)
    print("Winner:", winner)

    cardinal_social_welfare(names, winner, rankings)

    ordinal_social_welfare(names, orderRanking, winner)

