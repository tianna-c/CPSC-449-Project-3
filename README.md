###### Github Link: https://github.com/tianna-c/CPSC-449-Project-3
###### Program: Project 3
###### Authors: Tianna Cano, Patrick Lin, Raymond Magdaleno, Mark Wiedman
###### Date   : 4/29/2022 
 
  # Database and Microservices Initialization
- **You can clone this github repo or download and extract the folder onto your machine.**

- **It is required to run the AnswersDB.py and WordsDB.py files before running the procfile! _This is to create and initialize the databases if they do not already exist._**
<br> `$ python3 AnswersDB.py`
<br> `$ python3 WordsDB.py`

- **Then you run the procfile using foreman**
<br> `$ foreman start`
![VirtualBox_Tuffix 2020 Edition_08_04_2022_19_58_09](https://user-images.githubusercontent.com/39601543/162554364-03d65d09-02ec-4de7-83a5-5adcbb0efc2d.png)

# Statistics Microservice
> Commands in File "Statistics.py"<br>
> Description: 'Statistics.py' handles presenting the statics of a user's game or record, and retrieving the top 10 users.
              
              /result/{current_user}  - Posting a win or loss for a particular game, along with a timestamp and number of guesses
              /getStats/  - Retrieving the statistics for a user
              /toptens/  - Retrieving the top 10 users by number of wins or longest streak

1. /result/{current_user}
      The '/result/{current_user}' command will post a win or loss for a particular game, along with a timestamp and number of guesses.

2. /getStats/
      The 'getStats' command will retrieve the statistics for a user using a structured format.

3. /toptens/
      The 'toptens' command will retrieving the top 10 users by number of wins and by longest streak.
   
