# About this project

This repository is for improvements made on the coursework that was completed for the Advanced Web Technologies (SET09103) module at Edinburgh Napier University. It was developed using Python Flask and Levinux.

## What does the app do? 

This prototype web app is based on the popular website Reddit. It is a social news website and forum where posts are socially curated and promoted by site members. The site is composed of various sub-communities, known as "subreddits." Each subreddit has a specific topic such as technology, politics or movies. Members of the site can submit content which is then voted upon by other members with the goal of sending well-regarded posts to the top of the site's front page. The aim of this project was to recreate the fundamental architecture of Reddit within a Python Flask application. The application will be referred to as Reddit Clone throughout this report. 

## Development process

### Framework

The Reddit Clone web-app was built upon the Flask micro-framework – a lightweight framework for Python which makes use of the Werkzeug utility library and Jinja2 templating engine (https://flask.palletsprojects.com/). The application was developed within the portable Linux distribution Levinux. This allowed for compatibility across different machines during the development process.

### Database

The underlying functionality of the Reddit Clone web-app is highly reliant on its database structure. In order to implement integral features such as user authentication, the creation of subreddits and the ability to submit posts and comments, an SQLite database was created. The database consists of four tables – users, subreddits, posts, and comments. Relationships were made between the tables to link data, for example, comments are related to posts, and posts are related to comments. 

### Error handling

When developing an application, precautions must be must be taken to prevent users from experiencing errors. In the event that errors are encountered, users should be given an appropriate message to inform them of what has gone wrong.  

An example of this can be seen if a user attempts to log in with an incorrect username or password. The user is directed back to the login page with a displayed error message.

Another example of this can be experienced if the user attempts to cast a vote on a post without being logged in. Rather than nothing happening, and the user being left confused, a login form is displayed within a modal pop-up and conveniently allows the user to sign in. 

### Templates

The application has been built within Flask, which itself includes the Jinja2 templating engine. This allows many additional features to be used, directly within the HTML code, such as ‘for loops’ and ‘if statements’, which proved to be extremely beneficial when developing the application. In addition, Jinja2 allows extending of templates, which means that one base file can be used to store the information which will remain the same across all pages, and additional pages can be extended to it. 

### Logging 

Logging has been used to keep track if various things that users encounter when using the application, for example, if a user enters an incorrect password, a log is written including the time, user and route for which the error occurred. 

### Unit testing

Unit testing has been implemented in order to test the functionality of various features during development. For example, a test is run to check if users are redirected when attempting to access restricted pages. Another test is run to check the expected results when users attempt to log in with incorrect details, and another test to ensure that the front page is functioning properly. 

## Design

### Branding/style

The Bootstrap front-end framework was implemented for the design of this web application. Bootstrap is useful for creating a basic consistent layout across all pages when developing prototype applications. Another valuable feature of Bootstrap is its responsiveness. This means that the web-app displays well across various sized devices.  

A custom logo was created to brand the application. The logo consists of two arrows, depicting an ‘upvote’ and ‘downvote’ as featured next to each post in the web-app.

### Posts & comments

Comment threads are displayed beneath each post. Each level of comment has a different colour, to help the user differentiate between which comment is replying to which. 
 
### Voting

Voting arrows are displayed next to each post. If a user click to vote, the arrow changes colour. The vote is written to the database, so if the user revisits the page at a later date, the post remains voted on. 

### Accessibility 

Accessibility is an important issue when designing for the web, as users with disabilities must be able to use the application. To make the web application more accessible, alternative text has been added to images. The hierarchy of the HTML also allows users to navigate between pages using a keyboard.  


## How do I use the app? 

* Clone the repo
* Navigate to the 'src' folder
* Type "python app.py"
* Wait a few seconds for the app to start running
* In your browser, navigate to localhost:5000
