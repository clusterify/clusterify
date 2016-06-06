Clusterify
==========
What is it?
-------------
Clusterify is a better way to meet other programmers working with the same technologies you are. Open source projects are great, but they usually require large investments of time. The idea here is to keep it short, just a couple hours per project. If you have a cool idea for a short project, and want to work on it with a couple other programmers, sign up here to get started!

The site is also about learning and experimenting, sharing tips along the way with others. And if you just want to share some ideas but don't have time to work on them, you can do this too: just select "I'm not participating" in the "new project" form. Others can then come and administer the project.

It's up to you to decide what collaboration tools you're going to use, what language, what framework, what repository...

Quick history...
----------------
Clusterify.com is derived from an idea proposed by François Savard on Hacker News and Reddit in January 2009. Through interaction on the Hacker News thread, François met Aneesh Kulkarni, and both set out to implement the idea.

François worked about three weeks fulltime on the project and Aneesh helped out at times on nights/weekends until, in February 2009, they launched the project on Hacker News. After receiving much feedback, further tweaks were implemented during the following weeks. Meanwhile, about a hundred users signed up.

A few weeks later, Aneesh left the project. Shortly after, Sean Auriti contacted François to help with the site. After some discussion, they both agreed that responsibility for the site and project would be transfered to Sean. The transition happened around April 5, 2009, in the course of which the site changed servers and also became an open source project.

Clusterify can easily be deployed to Heroku.

This application supports the [Getting Started with Python on Heroku](https://devcenter.heroku.com/articles/getting-started-with-python) article - check it out.

## Running Locally

Make sure you have Python [installed properly](http://install.python-guide.org).  Also, install the [Heroku Toolbelt](https://toolbelt.heroku.com/) and [Postgres](https://devcenter.heroku.com/articles/heroku-postgresql#local-setup).

```sh
$ git clone git@github.com:heroku/python-getting-started.git
$ cd python-getting-started

$ pip install -r requirements.txt

$ createdb python_getting_started

$ python manage.py migrate
$ python manage.py collectstatic

$ heroku local
```

Your app should now be running on [localhost:5000](http://localhost:5000/).

## Deploying to Heroku

```sh
$ heroku create
$ git push heroku master

$ heroku run python manage.py migrate
$ heroku open
```
or

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

## Documentation

For more information about using Python on Heroku, see these Dev Center articles:

- [Python on Heroku](https://devcenter.heroku.com/categories/python)
