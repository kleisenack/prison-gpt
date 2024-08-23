# Chatbots Playing Games
Konrad Eisenack (August 2024)

- Steps 0-3 below help you setting up Python and GitHub (boring, if you know Python)
- Steps 4-5 set up the ChatGPT API (which needs to be bought)
- Steps 6-7 show you how to use the Python scripts

## Installation & Use

### 0. Get a Python IDE (recommended)

Helps you a lot when writing code and modifying the project.

- [PyCharm](https://www.jetbrains.com/pycharm/download) Community Edition OR
- [VSCode](https://code.visualstudio.com/download) with Python extensions

### 1. Clone or Download the Project from GitHub

You need to get the project files on your computer.

- download the project by clicking the green `Code` button and then the `Download ZIP` button on GitHub OR
- clone the project by running the command `git clone https://github.com/kleisenack/prison-gpt` in your terminal to the desired location

### 2. Install Rye

This tool manages the setup of Python for the project and installs all libraries and dependencies required by the project.

- [Rye Installation Instructions](https://rye-up.com/guide/installation/)

### 3. Setup the Project with Rye

Setup Python for the project and install all required dependencies.

- from a terminal inside the project folder run `rye sync`

### 4. Get an OpenAI API Key

This project uses the AI from OpenAI, which can be accessed through its API, which requires a key for authentication.
> The API costs money (you will need to pay per token).

- create or login to an OpenAI account
- create an API key in the dashboard

### 5. Create an `.env` File With the API Key

The project needs to be told the API key in a secure way.

- copy the `.env.example` file
- rename it to just `.env`
- replace `put your API key here` with your API key

### 6. Run the project

from a terminal in the project folder:

- run `rye run play` to let the ai play the games

### 7. Design Own Experiments

The prompts for the game rules can be found under [/src/messages](/src/messages) in separate files.
You can edit them or create new files. The files must end with `.md`.

The prompts for the player roles can be found under [/src/messages/roles](/src/messages/roles).
They also end with `.md` and you can edit them or create new ones.

For your own experiments you need to edit [main.py](/src/prison_gpt/main.py) script.
Starting from line 14 (`# Settings to configure`) you can change the input files for role and rule descriptions and the output file name.
The output file (a `.csv`) is stored under [data](/src/data).
The game matrix can be modified by changing the function `_game_matrix` just below the settings to configure.
