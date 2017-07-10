# Objective: match the appid of demos and games.

def to_integer(my_str):
    return int(my_str.replace(',', ''))


def to_percentage(my_str):
    return float(my_str.strip("%")) / 100


def load_game_file(input_filename):
    # Read the TXT file containing the list of Steam games
    #
    # Input:    input_filename
    # - a text file, manually copied from SteamDB at steamdb_game_url:
    steamdb_game_url = "https://steamdb.info/stats/gameratings/?all"
    # NB: To download input_filename, you need to log in using your own Steam account on
    #     steamdb_game_url and then select to show all in the dropdown menu.
    #
    # Output:   game_data
    # - a Python dictionary

    game_data = dict()

    with open(input_filename, 'r', encoding="utf8") as infile:
        for line in infile:
            items = line.strip().split("\t")
            stripped_items = list(map(str.strip, items))

            appid = stripped_items[1]
            game_name = stripped_items[2]

            game_data[appid] = dict()
            game_data[appid]['appid'] = to_integer(appid)
            game_data[appid]['name'] = game_name
            game_data[appid]['num_positive_reviews'] = to_integer(stripped_items[3])
            game_data[appid]['num_negative_reviews'] = to_integer(stripped_items[4])
            game_data[appid]['wilson_score'] = to_percentage(stripped_items[-2])
            game_data[appid]['steam_score'] = to_percentage(stripped_items[-1])

    print('#games =', len(game_data))

    return game_data


def load_demo_file(input_filename):
    # Read the TXT file containing the list of Steam demos
    #
    # Input:    input_filename
    # - a text file, manually copied from SteamDB at steamdb_demo_url:
    steamdb_demo_url = "https://steamdb.info/search/?a=app&q=&type=3&category=0"
    # NB: To download input_filename, you need to log in using your own Steam account on
    #     steamdb_demo_url and then select to show all in the dropdown menu.
    #
    # Output:   demo_data
    # - a Python dictionary

    demo_data = dict()

    with open(input_filename, 'r', encoding="utf8") as infile:
        for line in infile:

            items = line.strip().split("\t")
            stripped_items = list(map(str.strip, items))

            appid = stripped_items[0]
            demo_name = stripped_items[2]

            # Keywords not included in other keywords
            unambiguous_keywords = ["Demo", "DEMO", "demo",
                                    "Free Trial", "[FREE TRIAL]", "DirectX10 Trial", "Lite",
                                    "Pre-Alpha", "Public Beta", "Press", "Playable Trailer"]
            # Short keywords included in a few longer keywords
            ambiguous_keywords = ["Free", "Beta"]

            if any(keyword in demo_name for keyword in unambiguous_keywords):
                game_name = demo_name
                for keyword in unambiguous_keywords:
                    game_name = game_name.split(keyword)[0].strip()
            elif any(keyword in demo_name for keyword in ambiguous_keywords):
                game_name = demo_name
                for keyword in ambiguous_keywords:
                    game_name = game_name.split(keyword)[0].strip()
            elif "(" in demo_name:
                game_name = demo_name.split("(")[-1].strip(")")
            else:
                # print(demo_name)
                continue

            demo_data[appid] = dict()
            demo_data[appid]['appid'] = to_integer(appid)
            demo_data[appid]['name'] = demo_name
            demo_data[appid]['game_name'] = game_name

    print('#demos =', len(demo_data))

    return demo_data


def match_appid(game_data, demo_data):
    match_data = dict()

    for game in game_data.values():
        if game["name"] in [v["game_name"] for v in demo_data.values()]:
            demo_appid = [v["appid"] for v in demo_data.values() if game["name"] == v["game_name"]]

            appid = str(game["appid"])
            match_data[appid] = game
            match_data[appid]["demo_appid"] = demo_appid[0]

    print('#games matched with demos =', len(match_data))

    unused_demo_data = dict()

    for demo in demo_data.values():
        demo_appid = demo["appid"]
        if not(demo_appid in [v["demo_appid"] for v in match_data.values()]):
            unused_demo_data[str(demo_appid)] = dict()
            unused_demo_data[str(demo_appid)] = demo_data[str(demo_appid)]

    print('#demos not matched with any game=', len(unused_demo_data))

    return (match_data, unused_demo_data)

def print_match_data(match_data, output_filename=None):
    base_steam_store_url = "http://store.steampowered.com/app/"
    width = 40

    computeScore = lambda x: x["wilson_score"]

    # Rank all the Steam games
    sortedValues = sorted(match_data.values(), key=computeScore, reverse=True)

    current_rank = 0
    for game in sortedValues:
        game_appid = str( game["appid"] )
        game_name = game["name"]
        demo_appid = str( game["demo_appid"] )
        current_rank += 1

        game_url = base_steam_store_url + game_appid
        demo_url = base_steam_store_url + demo_appid

        if output_filename is None:
            print('{:04}'.format(current_rank) + ".\t[" + game_name + "](" + game_url + ")"
                  + " -> [demo](" + demo_url + ")" )
        else:
            with open(output_filename, 'a', encoding="utf8") as outfile:
                print('{:04}'.format(current_rank) + ".\t[" + game_name + "](" + game_url + ")"
                      + " -> [demo](" + demo_url + ")", file=outfile)

if __name__ == "__main__":
    game_filename = "top_rated_games_on_steam.txt"
    demo_filename = "demo_on_steam.txt"
    output_filename = "wilson_ranking.txt"


    games = load_game_file(game_filename)
    demos = load_demo_file(demo_filename)

    (matches, unused_demo_data) = match_appid(games, demos)

    print(unused_demo_data)

    with open(output_filename, 'w', encoding="utf8") as outfile:
        print_match_data(matches, output_filename)
