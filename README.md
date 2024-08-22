# prison-gpt

## Development Setup

### 0. Get a Python IDE (recommended)

Helps you a lot when writing code and modifying the project.

- [PyCharm](https://www.jetbrains.com/pycharm/download) Community Edition OR
- [VSCode](https://code.visualstudio.com/download) with Python extensions

### 1. Clone or Download the Project

You need to get the project files on your computer.

- clone the project by running the command `git clone https://github.com/kleisenack/prison-gpt` in your terminal to the desired location OR
- download the project by clicking the green `Code' button and then the `Download ZIP' button on GitHub.

### 2. Installing Rye

This tool manages the setup of Python for the project and installs all dependencies required by the project.

- [Rye Installation Instructions](https://rye-up.com/guide/installation/)

### 3. Setup the project with Rye

Setup Python for the project and install all required dependencies.

- from a terminal inside the project folder, run `rye sync`.

### 4. Get an OpenAI API Key

This project uses the AI from OpenAI, which can be accessed through its API, which requires a key for authentication.

- create or login to an OpenAI account
- create an API key in the Dashboard.

### 5. Create an `.env` File With the API Key

The project needs to be told the API key in a secure way.

- copy the `.env.example` file
- rename it to just `.env`
- replace `put your api key here` with your api key

### 6. Run the project

from a terminal in the project folder:

- run `rye run play` to let the ai play the games
- run `rye run analyze` to analyze a given game
