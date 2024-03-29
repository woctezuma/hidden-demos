# Objective: match the appid of demos and games.
from pathlib import Path


def to_integer(my_str):
    return int(my_str.replace(',', ''))


def to_percentage(my_str):
    return float(my_str.strip('%')) / 100


def load_game_file(input_filename):
    # Read the TXT file containing the list of Steam games
    #
    # Input:    input_filename
    # - a text file, manually copied from SteamDB at steamdb_game_url:
    steamdb_game_url = 'https://steamdb.info/stats/gameratings/?all'
    print('Please manually download data from: ' + steamdb_game_url)
    # NB: To download input_filename, you need to log in using your own Steam account on
    #     steamdb_game_url and then select to show all in the dropdown menu.
    #
    # Output:   game_data
    # - a Python dictionary

    game_data = {}

    with Path(input_filename).open(encoding='utf8') as infile:
        for line in infile:
            items = line.strip().split('\t')
            stripped_items = list(map(str.strip, items))

            appid = stripped_items[1]
            game_name = stripped_items[2]

            game_data[appid] = {}
            game_data[appid]['appid'] = to_integer(appid)
            game_data[appid]['name'] = game_name
            game_data[appid]['num_positive_reviews'] = to_integer(stripped_items[3])
            game_data[appid]['num_negative_reviews'] = to_integer(stripped_items[4])
            game_data[appid]['wilson_score'] = to_percentage(stripped_items[-2])
            game_data[appid]['steam_score'] = to_percentage(stripped_items[-1])

    print('#games =', len(game_data))

    return game_data


def load_demo_file(input_filename, verbose=False):
    # Read the TXT file containing the list of Steam demos
    #
    # Input:    input_filename
    # - a text file, manually copied from SteamDB at steamdb_demo_url:
    steamdb_demo_url = 'https://steamdb.info/search/?a=app&q=&type=3&category=0'
    print('Please manually download data from: ' + steamdb_demo_url)
    # NB: To download input_filename, you need to log in using your own Steam account on
    #     steamdb_demo_url and then select to show all in the dropdown menu.
    #
    # Output:   demo_data
    # - a Python dictionary

    demo_data = {}

    with Path(input_filename).open(encoding='utf8') as infile:
        for line in infile:
            items = line.strip().split('\t')
            stripped_items = list(map(str.strip, items))

            appid = stripped_items[0]
            demo_name = stripped_items[2]

            # Keywords not included in other keywords
            unambiguous_keywords = [
                'Demo',
                'DEMO',
                'demo',
                'Christmas Edition',
                'Free Trial',
                '[FREE TRIAL]',
                'DirectX10 Trial',
                'Lite',
                'Pre-Alpha',
                'Public Beta',
                'Press',
                'Playable Trailer',
            ]
            # Short keywords included in a few longer keywords
            ambiguous_keywords = ['Free', 'Beta']

            if any(keyword in demo_name for keyword in unambiguous_keywords):
                game_name = demo_name
                for keyword in unambiguous_keywords:
                    game_name = game_name.split(keyword)[0].strip()
            elif any(keyword in demo_name for keyword in ambiguous_keywords):
                game_name = demo_name
                for keyword in ambiguous_keywords:
                    game_name = game_name.split(keyword)[0].strip()
            elif '(' in demo_name:
                game_name = demo_name.split('(')[-1].strip(')')
            elif demo_name.lower()[-1] == 'd':
                game_name = demo_name[:-1].strip()
                if verbose:
                    print('Demo name ends with a d:\t' + demo_name)
            else:
                base_steam_store_url = 'https://store.steampowered.com/app/'
                demo_url = base_steam_store_url + appid
                if verbose:
                    print(
                        'Demo name is not explicit:\t'
                        + '['
                        + demo_name
                        + ']('
                        + demo_url
                        + ')',
                    )
                game_name = demo_name

            demo_data[appid] = {}
            demo_data[appid]['appid'] = to_integer(appid)
            demo_data[appid]['name'] = demo_name
            demo_data[appid]['game_name'] = game_name

    print('#demos =', len(demo_data))

    return demo_data


def match_appid(game_data, demo_data):
    match_data = {}

    game_name_inferred_from_demo_name = [v['game_name'] for v in demo_data.values()]

    for appid, game in game_data.items():
        game_true_name = game['name']
        if game_true_name in game_name_inferred_from_demo_name:
            demo_appid = [
                v['appid']
                for v in demo_data.values()
                if (v['game_name'] == game_true_name)
            ]
            match_data[appid] = game
            match_data[appid]['demo_appid'] = demo_appid[0]

    print('#games matched with demos =', len(match_data))

    # Demo data not matched with any rated game is usually due to the fact the game is not released yet, and thus is not
    # rated yet. Therefore, the game can exist and have a store page, but without being in top_rated_games_on_steam.txt.

    unused_demo_data = {}

    appid_for_matched_demo = [v['demo_appid'] for v in match_data.values()]

    for demo_appid_str in demo_data:
        if demo_data[demo_appid_str]['appid'] not in appid_for_matched_demo:
            unused_demo_data[demo_appid_str] = demo_data[demo_appid_str]

    print('#demos not matched with any rated game=', len(unused_demo_data))

    return match_data, unused_demo_data


def get_wilson_score(x):
    return x['wilson_score']


def get_game_name(x):
    return x['game_name']


def print_match_data(match_data, output_filename=None):
    base_steam_store_url = 'https://store.steampowered.com/app/'
    steam_install_command = 'steam://install/'

    # Rank all the Steam games
    sorted_values = sorted(match_data.values(), key=get_wilson_score, reverse=True)

    current_rank = 0
    for game in sorted_values:
        game_appid = str(game['appid'])
        game_name = game['name']
        demo_appid = str(game['demo_appid'])
        current_rank += 1

        game_url = base_steam_store_url + game_appid
        demo_url = base_steam_store_url + demo_appid
        demo_install_command = steam_install_command + demo_appid

        if output_filename is None:
            print(
                f'{current_rank:04}'
                + '.\t['
                + game_name
                + ']('
                + game_url
                + ')'
                + ' -> [demo]('
                + demo_url
                + ') + '
                + demo_install_command,
            )
        else:
            with Path(output_filename).open('a', encoding='utf8') as outfile:
                print(
                    f'{current_rank:04}'
                    + '.\t['
                    + game_name
                    + ']('
                    + game_url
                    + ')'
                    + ' -> [demo]('
                    + demo_url
                    + ') + '
                    + demo_install_command,
                    file=outfile,
                )


def print_unmatched_data(unused_demo_data, output_filename=None):
    base_steam_store_url = 'https://store.steampowered.com/app/'
    steam_install_command = 'steam://install/'

    # Rank all the Steam games
    sorted_values = sorted(unused_demo_data.values(), key=get_game_name)

    current_rank = 0
    for demo in sorted_values:
        demo_appid = str(demo['appid'])
        game_name = demo['game_name']
        current_rank += 1

        demo_url = base_steam_store_url + demo_appid
        demo_install_command = steam_install_command + demo_appid

        if output_filename is None:
            print(
                f'{current_rank:04}'
                + '.\t['
                + game_name
                + ']('
                + demo_url
                + ')  + '
                + demo_install_command,
            )
        else:
            with Path(output_filename).open('a', encoding='utf8') as outfile:
                print(
                    f'{current_rank:04}'
                    + '.\t['
                    + game_name
                    + ']('
                    + demo_url
                    + ')  + '
                    + demo_install_command,
                    file=outfile,
                )


def main(verbose=False):
    game_filename = 'top_rated_games_on_steam.txt'
    demo_filename = 'demo_on_steam.txt'
    output_filename = 'wilson_ranking.txt'
    error_filename = 'unmatched_demos.txt'

    games = load_game_file(game_filename)
    demos = load_demo_file(demo_filename, verbose)

    (matches, unused_demo_data) = match_appid(games, demos)

    with Path(output_filename).open('w', encoding='utf8') as _:
        print_match_data(matches, output_filename)

    with Path(error_filename).open('w', encoding='utf8') as _:
        print_unmatched_data(unused_demo_data, error_filename)

    return True


if __name__ == '__main__':
    main()
