# Lab 2: Login & To-Do Application

## 1. Team Members:
# -->student 1 
name : Sohila Wael 
id : 2304073
# -->student 2
name : Omar Mohamed
id :2304093

## 2. Technology:
- Back end: Python 3 with Flask. Passwords are hashed with `bcrypt`. MySQL is accessed with `PyMySQL` using plain SQL with parameters (no ORM).
- Front end: HTML, CSS and JavaScript, with Jinja templates.
- Database: MySQL 8.0, database `registration`.

## 3. How to Run:
1. Install Python 3 and MySQL Server.
2. Clone the repository and open a terminal in its folder.
3. Create and activate a virtual environment, then install the libraries:
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
4. Create the database and tables by running the schema in MySQL:mysql -u root -p < database/schema.sql
5. Copy `.env.example` to `.env` and fill in your values (your MySQL password and a long random `SECRET_KEY`): copy .env.example .env
6. Start the server:python app.py
7. Open `http://127.0.0.1:5000/register` in the browser.


## 4. Features:
- R1 = Register with name, e-mail, password and confirm password. A duplicate e-mail shows `Email Already Exists`. After registering, the user is logged in and sees the list.
- R2 = Login with e-mail and password. A wrong e-mail or a wrong password shows the same message, `Invalid email or password`. Logout ends the session.
- R3 = The list is private. A visitor who is not logged in is redirected to the login page, and each user sees only their own to-dos, newest first.
- R4 = Add a to-do.
- R5 = Edit a to-do title.
- R6 = Mark a to-do as done or not done.
- R7 = Delete a to-do, with an "Are you sure?" confirmation.
- R8 = Validation in the browser (JavaScript) and again on the server, with the exact messages from the lab.
- R9 = Passwords are stored as bcrypt hashes. Only the given queries are used, always with parameters, and `user_id` always comes from the session.
- R10 = A consistent, responsive interface that works on a 360 px screen, with error messages, a visible state for done to-dos, an empty-list message, and the user's name with a logout button.
- Bonus:counter showing how many to-dos are still open.

## 5. Screenshots: 
 in foldar screenshots

## 6. Answers

(a) Why do UPDATE and DELETE contain `AND user_id = ?`, and what changes if you remove it?
The id of a to-do comes from the browser, so anybody can send somebody else's number. Adding `AND user_id = ?` (the id of the logged-in user, taken from the session and never from a form) makes the statement change zero rows when the to-do is not yours. Without it, any logged-in user could edit or delete another user's to-dos just by changing the number in the request.

(b) What happens if you insert a to-do for a `user_id` that does not exist, and which constraint of the lecture is that?
MySQL rejects the INSERT with error 1452: "Cannot add or update a child row: a foreign key constraint fails". This is the foreign key constraint (referential integrity): every to-do must belong to exactly one existing user.

(c) Why do you store a hash and not the password?
If the database is leaked, anyone who reads it would see all the real passwords. A bcrypt hash cannot be reversed to get the original password. It is also salted, so two users with the same password get different hashes, and it is slow on purpose, which makes guessing attacks expensive. To log in, the library compares the typed password with the stored hash (`bcrypt.checkpw`).

(d) The `name` column is NOT NULL: why did you still need your own check for an empty name?
`NOT NULL` only means that the column must have a value. An empty text `''` is a value, not NULL, so MySQL accepts it. Only our own checks (in JavaScript in the browser and again on the server) can refuse an empty name.
