# Toss Game

game that all participants winning. you can select up to 80% percent of winning.\
low the risk **or** make it maximum you are the controller here.

## Getting Started

### Prerequisites

- [Python3.6](https://www.python.org/downloads/) or later

### Installing

#### Clone The repository and install dependencies

``` bash
git clone https://github.com/mohamed17717/Toss.git <filename>
cd <filename>
pip install -r requirements.txt
```

#### Set environment variables

``` bash
export FLASK_APP=app.py
export FLASK_DEBUG=1
export DATABASE_URL=postgres://egikqvyqcmpqpo:fb7a420683d8e9a41735e4f985c02a9a202ae74e2020935a4a27158c225f203a@ec2-46-137-121-216.eu-west-1.compute.amazonaws.com:5432/df44rp66emil5p
```

#### Run

``` bash
flask run
```

## Deployment

I will deploy it soon, when i know how :"""

## Features

1. Login system
   - Register
   - Login
   - Sessions

2. Time system to handle different user's timezones

3. Random system to choose the winner

4. User system
   1. User can create games
      - Set Whatever rules he want
      - limitation for user to create more than 5 up games to stop spamming

   2. User can delete games
      - user must be the creator
      - no other users joined

   3. User can join the game
      - Unless it is the last 15 min for the game he **can't**

   4. User can dare the game
      - Daring in the first 15 min user joined
      - User can't dare if it the last 15 min of a game

   5. User can Filter games to search faster

5. Pages
   1. home page
      - with
        - simple tables for make it easy reading data of game
        - reponsive table remove less important clms in small windows
      - to show
        - all up games
        - all games you in
   2. Profile to track your winnig and loses
   3. Game page showing all information about the game
   4. wallet to track money in use and total money

## Built With

- **Flask** -  The web framework used
- **Postgre + SQL** - For database
- **Bootstrab** - CSS framework

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
