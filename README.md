# Hidden Demos

[![Build status][Build image]][Build]
[![Code coverage][Codecov image]][Codecov]

  [Build]: <https://github.com/woctezuma/hidden-demos/actions>
  [Build image]: <https://github.com/woctezuma/hidden-demos/workflows/Python package/badge.svg?branch=master>

  [PyUp]: https://pyup.io/repos/github/woctezuma/hidden-demos/
  [Dependency image]: https://pyup.io/repos/github/woctezuma/hidden-demos/shield.svg
  [Python3 image]: https://pyup.io/repos/github/woctezuma/hidden-demos/python-3-shield.svg

  [Codecov]: https://codecov.io/gh/woctezuma/hidden-demos
  [Codecov image]: https://codecov.io/gh/woctezuma/hidden-demos/branch/master/graph/badge.svg

This repository contains code to compute a ranking of Steam games which offer a demo.

## Game scoring ##

The ranking is based on the Wilson score.

## Data source ##

The quality measure comes from [SteamDB](https://steamdb.info/stats/gameratings/)

The data is included along the code in this repository, as downloaded on July 10, 2017.

## Requirements ##

This code is written in Python 3.

## Results ##

As of July 10, there are 14262 games, 1953 demos, but only 1376 demos matched with rated games. Indeed, 577 demos could not be matched with any rated game:
- 7 demos had weird names, from which I could not automatically infer the name of the original game,
	* [ValveTestApp398280](http://store.steampowered.com/app/398280)
	* [Thunderbird: The Introduction](http://store.steampowered.com/app/415520)
	* [Doll City VR](http://store.steampowered.com/app/468180)
	* [DIVO](http://store.steampowered.com/app/213430)
	* [SiN Episodes: Emergence German](http://store.steampowered.com/app/1306)
	* [Chaos on Deponia](http://store.steampowered.com/app/224100)
	* [Zombie Driver](http://store.steampowered.com/app/31419)
- 570 demos could be matched, but the matched games were not yet released, a foritori not yet rated, and thus could not be ranked.

## References ##
* [a NeoGAF post](http://www.neogaf.com/forum/showpost.php?p=243096033&postcount=1579).

