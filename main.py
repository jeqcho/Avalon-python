def ask_player(i, n):
    return str(input("Who was playing in the round? " + str(i + 1) + "/" + str(n) + ": ")).lower()


def get_name(i):
    return str(input("Please enter name of player " + str(i + 1) + ": ")).lower()


class Constraint:
    def __init__(self, suspects, num_fail):
        self.suspects = suspects
        self.fails = num_fail


class Accusation:
    def __init__(self, accuser, accused, verdict):
        self.accuser = accuser
        self.accused = accused
        self.verdict = verdict


def get_combo_id(evil_list):
    combo_id = ""
    for evil in evil_list:
        combo_id += str(evil)
    return combo_id


class Game:
    num_players = 0
    #   vector<pair<vector<string>, int>> constraints
    # list of teammates, number of fail
    constraints = []
    names = []
    name_to_id = {}
    quest_layout = {
        5: [2, 3, 2, 3, 3],
        6: [2, 3, 4, 3, 4],
        7: [2, 3, 3, 4, 4],
        8: [3, 4, 4, 5, 5],
        9: [3, 4, 4, 5, 5],
        10: [3, 4, 4, 5, 5]

    }
    evil_cnt = {
        5: 2,
        6: 2,
        7: 3,
        8: 3,
        9: 3,
        10: 4
    }
    combo = {}
    combo_sz = 0
    accusations = []
    bad = []
    failed = False

    def __init__(self):
        self.num_players = int(input("How many players are playing?"))
        if self.num_players > 10 or self.num_players < 5:
            print("This program can only handle 5 to 10 players. You entered " + str(self.num_players) + " players.")
            self.failed = True
            return
        self.num_evil = self.evil_cnt[self.num_players]
        self.players_per_round = self.quest_layout[self.num_players]
        print("Number of evil characters is " + str(self.num_evil))
        for i in range(self.num_players):
            name = get_name(i)
            error1 = name == ""
            error2 = name in self.names
            while error1 or error2:
                if error1:
                    print("Name cannot be empty")
                else:
                    print(name + " is already added. Type another player")
                name = get_name(i)
                error1 = name == ""
                error2 = name in self.names
            self.names.append(name)

        for i in range(len(self.names)):
            self.name_to_id[self.names[i]] = i

    def end_round(self, round_num):
        print("Round " + str(round_num + 1))
        num_mate = self.players_per_round[round_num]
        num_fail = int(input("Please enter number of failures out of " + str(num_mate) + ": "))
        while num_fail > num_mate or num_fail < 0:
            print(str(num_fail) + " is not in the range 0 to " + str(num_mate))
            num_fail = int(input("Please enter number of failures out of " + str(num_mate) + ": "))

        current_players = []
        for i in range(num_mate):
            name = ask_player(i, num_mate)
            error1 = name not in self.names
            error2 = name in current_players
            while error1 or error2:
                if error1:
                    print(name + " is not found in name list. Check for typo and type again")
                else:
                    print(name + " is already added. Type another player")
                name = ask_player(i, num_mate)
                error1 = name not in self.names
                error2 = name in current_players
            current_players.append(name)

        players_id = []
        for player in current_players:
            players_id.append(self.name_to_id[player])

        if round_num > 0:
            accuse = str(input("Is the Lady of the Lake used? (Y/N)"))
            if accuse == "Y":
                while True:
                    accuser = str(input("Who used it?"))
                    if accuser in self.names:
                        break
                    print(accuser + " is not in the namelist")
                while True:
                    accused = str(input("Who was tested?"))
                    if accused in self.names:
                        break
                    print(accused + " is not in the namelist")
                while True:
                    verdict = str(input("What did " + str(accuser) + " say? (G/B)"))
                    if verdict in ["G", "B"]:
                        break
                    print(verdict + " is either G (Good) or B (Bad)")
                self.accusations.append(Accusation(accuser, accused, verdict))

        self.add_constraint(players_id, num_fail)
        self.combo = {}
        self.combo_sz = 0
        self.bad = [0] * self.num_players
        self.recur(0, [])
        if self.combo_sz > 0:
            print("Probability of being an evil character")
            for player in range(self.num_players):
                self.bad[player] /= self.combo_sz
                self.bad[player] *= 100
                self.bad[player] = round(self.bad[player], 2)
                print(self.names[player] + ": " + str(self.bad[player]) + "%")
            most_prob_combo = max(self.combo, key=self.combo.get)
            print("Most probable combination of evil characters:")
            combo_prob = round(self.combo[most_prob_combo] / self.combo_sz * 100, 2)
            print(self.id_to_str(most_prob_combo), str(combo_prob) + "%")
        else:
            print("The program failed because some good guy put failure or lied")
            return 1
        return 0

    # use recursion for dynamic loops
    def recur(self, current, evil_list):
        if len(evil_list) == self.num_evil:
            self.process_combo(evil_list)
            return
        if current >= self.num_players:
            return
        self.recur(current + 1, evil_list)
        new_list = evil_list.copy()
        new_list.append(current)
        self.recur(current + 1, new_list)

    def process_combo(self, evil_list):
        if self.validate(evil_list):
            combo_id = get_combo_id(evil_list)
            if combo_id in self.combo:
                self.combo[combo_id] += 1
            else:
                self.combo[combo_id] = 1
            self.combo_sz += 1
            for evil in evil_list:
                self.bad[evil] += 1

    def add_constraint(self, players_id, num_fail):
        self.constraints.append(Constraint(players_id, num_fail))

    def validate(self, evil_list):
        for constraint in self.constraints:
            num_fail = constraint.fails
            for suspect in constraint.suspects:
                if suspect in evil_list:
                    num_fail -= 1
            if num_fail > 0:
                return False
        for accusation in self.accusations:
            if accusation.accuser not in evil_list:
                is_evil = accusation.accused in evil_list
                said_evil = accusation.verdict == "B"
                if is_evil != said_evil:
                    return False
        return True

    def id_to_str(self, most_prob_combo):
        names = ""
        for char in most_prob_combo:
            names += self.names[int(char)] + ' '
        return names


def main():
    game = Game()

    if game.failed:
        return 0

    for i in range(5):
        if game.end_round(i) == 1:
            break


if __name__ == "__main__":
    main()
