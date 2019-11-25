# quizbot
a python chat bot. currently supports GroupMe and Discord
current version 0.6b

This project started as a way to quiz SECC Bible Bowlers on their material, but it can also be used for other quizzes/study groups.

# **To Use**
- Clone this repository
- Rename example_config.json to config.json
- Add your groupme bot name, id, and groupid to it and change the listening port to the one you will be using
- If you are using the quiz section you also will need to rename example_quiz_material.json to quiz_material.json
    - quiz_material.json uses a combination of sections and topics to create quizzes from, check examples for examples
- Run **pip install -r requirements**
- When all the requirements are installed, run **python3 run.py**
