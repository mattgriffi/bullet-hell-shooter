# Bullet Hell Shooter

This is a 2D boss-rush bullet-hell shooter. It features 3 unique bosses, each with 4 unique and challenging phases. It has local high scores, upgrades, customizable controls, and more.

I created this game as my final project for ECE102 Intro to Engineering Problem Solving in Fall of 2016. My professor said that we could make anything we wanted, and this professor was known for giving extra credit for flashy projects. For a computer science major, what could be flashier than a video game? Thus, this project was born (over the course of a 4 month semester).

This project holds a special place in my heart because of what it represents. This was my first real project. When I started this project, I had only taken one CS class, Intro to Computer Science. I did not know Python, and I did not know how to make a video game. All I had was some fundamental knowledge, and a vision. Despite my lack of skills, I was able to make my vision a reality. The game as you see it here is exactly what I envisioned at the outset.

## Usage

To use this program, simply run it like any other Python program:

```sh
python main.py
```

## Installation

This program requires Python 3.

The required 3rd party module (pygame) is listed in requirements.txt and can be installed with the following command:

```sh
pip install -r requirements.txt
```

## Reflection/Postmortem

This game was my first real project. I was able to accomplish exactly what I set out to do without compromise. However, since I honestly had no idea what I was doing and had to figure everything out along the way, the code is utter trash. Some of the code in this project still gives me a headache when I look back on it, and I don't want to touch it with a 10 foot pole. So, instead of rewriting this project from scratch to make it pretty, I have chosen to preserve the code in all of its original beginner-level glory, and instead write a reflection. This reflection will go through the code file-by-file, method-by-method, and describe how I would do it differently if I were to tackle the same project today, 1 year later.

I'm sure that in 1 more year, I'll look back on this very reflection and wonder what I was thinking.

### shooter.py

This is the main file, which contains the main game loop... and a bunch of other stuff that shouldn't be there.

Before we even get to the first method, there's a bunch of pygame initialization code in the global scope. That should all be moved into main() so that it doesn't automatically run when the module is imported.

#### main

Ignoring MyLibrary for now, there's nothing really wrong with this method. It does some initial setup and then runs the game.

#### run_game

This method handles initial game setup, tracking boss progression, spawning powerups and enemies, updating and drawing all sprites and the UI, and ticking the framerate counter. Needless to say, "Single Responsibility Principle" was not part of my vocabulary at this point. This method should be split up into at least 5 different methods. All game logic should be moved elsewhere, while the main module handles updating and drawing things to the screen.

#### draw_hitbox

At some point during development I heard that having lots of small functions is a good idea. Judging by run_game, it was too little too late.

#### main_menu, highscores, game_over, options, upgrade_screen, ask_player_input

All UI code should be moved to a dedicated UI module. Also, the UI code should not not need to handle blitting things to the screen itself. All of the different UI screens could be incorporated into a single Interface class that uses the State pattern to keep track of which specific version should be returned to the main module for rendering. This would fix the problem of UI code being scattered all over the place.

You'll notice that all of the different non-game screens (main menu, upgrades, high scores, options) have an almost identical event-handling loop. This could better be handled with an EventHandler abstract class that uses the Template Method design pattern to provide hooks for all user input that I care about, then each UI screen would have its own EventHandler implementation that would handle the relevant user input appropriately.

#### check_for_events

At least I had the idea of making a separate function for gameplay-related event handling! This would be included in the Template scheme described above.

### mylibrary.py

The fact that I couldn't even come up with a good name for this probably says all you need to know. This god-class handles upgrades, some UI stuff, framerate limiting, random data management, sprite movement, math calculations, and more! Obviously, all of this stuff should be moved to either the appropriate modules, or to new, descriptively-named modules that each serve a single purpose.

In the class scope, we have a big OrderedDict to store all the upgrade information. I use an OrderedDict because the ordering of the upgrades is used when displaying them in the UI, which is obviously bad. It would be simpler to use a normal 2-dimensional dictionary, and have the strings available as public constants that the UI could use for accessing the data in whatever order it wants.

#### loading_screen

All the other screens (main menu, upgrades, high scores, etc.) are all in the main module, so why did I put the loading screen in mylibrary? This should be with the other UI methods in a dedicated UI class.

#### load_images

This is initialization code that could be handled in the main module or elsewhere. Note the laser beam code on line 197. This loads into memory 720 slightly rotated copies of a large laser beam image. This consumes several GBs of RAM. I did this because rotating an image in pygame is too slow, so I chose efficiency over space. I think the best solution to this problem is to write the game in something other than Python.

#### add_highscore, get_highscores

These could be moved to a separate module dedicated to handling high scores.

#### set_window_data

If all of the blitting were handled by the main module, there would be no need for a random library class to have knowledge of the program window.

#### normalize_target_fps

I had the idea for framerate that would scale dynamically to account for lag, but the idea didn't work out. Now the FPS code is all just a mess.

#### multi_shot_angles

Finally, after over 400 lines of code, we find a method that actually belongs in a generic library module! Even so, this could be moved to the shooting module, which I'll get to later.

#### normalize_angle

It didn't hit me until several months later that I could just mod by 360.

#### move_curve

This is where I almost independently invented integral calculus in order to implement a feature that I never even used.

#### move_point

This is sprite movement code that should not be here. It should be in a Sprite-based super class that all moving sprites inherit from.

#### bounce_angle

A great unsolved problem of this project. I wanted to have enemy projectiles realistically bounce off of the shield powerup, and I thought I could solve it with pure geometry and trigonometry. After taking physics, I realize that this problem would require momentum and vectors in order to solve properly.

### powerups.py

#### ShieldEffect

This thing was a nightmare. If I were to make another game, I would do it in an engine with built-in support for animations.

### enemy.py

This module contains Enemy, the super class for all of the enemies. At the time, I had just learned what an abstract class was, so I was excited to give it a try. I had the right idea for the most part, except...

#### shoot

Oh dear God what is this mess. This method is responsible for all shooting done by every enemy. All of the complex enemy attack patterns are handled in this method. Somehow. I'm not sure how. At the time, I was pretty proud of myself for accomplishing something seemingly so complicated with a relatively "simple" system. Looking at it now, it's an abomination.

All of the different shot patterns could be handled using the Strategy pattern, with bosses being composed with several different attack pattern implementations, and dynamically swapping between them throughout the fight.

### bullets.py

This is really an extension of what I said about enemy.py's shoot method. There should be a Bullet abstract class that handles all of the shared logic, then every different bullet behavior (homing, exploding, staggered homing, curved, etc.) should be a separate implementation. Combining the different Bullet implementations with different boss attack patterns would allow for greater flexibility, and would eliminate the incomprehensible mess that I concocted.


### bosses.py

Ignoring all of the FiringData and BulletData nonsense (which would be better handled with the system described above), there's not too much wrong with this module.

Most of the phase# methods in these classes should be split into several helper functions to handle movement, shooting, etc. separately.

#### Ring

This boss' minions should all be implemented as separate classes with their own, independent logic, rather than being mindless puppets controlled from within the boss' code. This would greatly simplify the code for the boss itself.
