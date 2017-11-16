# belote
A single-player implementation of the classic card game for 1 live player and three computer players (distributed in two teams). 

In order to play you need to install a Python 2.7 interpreter, and Pygame. To start the game, run belot.py. 

The game currently supports English and Bulgarian (more language support may be added later). 

This project is my most complicated work as a programmer so far. It started while I was learning initial programming in the Rice University online courses. They had a Blackjack implementation (where I got the card images, sorry!), and I got inspired to build a Belote implementation, starting from the basic classes we built during the course. I think the result is quite satisfactory, although lacking graphic polish. 

The strong sides of this project are:
- the AI, capable not only of fully following Belote rules, but also of implementing a clever strategy for winning, varying according to the current situation in the overal game (for example, the AI will bet differently in the beginning of a game, when they're leading, or trailing, and when the oponnent is close to winning the game). 
- custom-built Animations. I say this is a strength (although the animations are far from polished), because I didn't use any third-party engine, or any additional code libraries. I implemented an Animation class, capable of implementing movement of images across the screen, and growth of images. 

Enjoy, and feel free to comment! 
