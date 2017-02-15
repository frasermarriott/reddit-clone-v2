DROP TABLE if EXISTS users;

CREATE TABLE users (
  user_id TEXT UNIQUE,
  username TEXT UNIQUE,
  password TEXT,
  created_on TEXT
);

DROP TABLE if EXISTS subreddits;

CREATE TABLE subreddits (
  subreddit_id TEXT UNIQUE,
  subreddit_name TEXT UNIQUE,
  subreddit_title TEXT,
  subreddit_desc TEXT,
  subreddit_sidebar TEXT,
  subreddit_created_on TEXT,
  created_by_user TEXT
);

DROP TABLE if EXISTS posts;

CREATE TABLE posts (
  post_id TEXT UNIQUE,
  related_subreddit_id TEXT,
  related_subreddit_name TEXT,
  related_user_id TEXT,
  post_type TEXT,
  post_title TEXT,
  url_friendly_title TEXT,
  post_link TEXT,
  post_textarea TEXT,
  post_timestamp TEXT,
  post_votes TEXT,
  upvoted_by_user TEXT,
  downvoted_by_user TEXT
);

DROP TABLE if EXISTS comments;

CREATE TABLE comments (
  comment_id TEXT UNIQUE,
  related_post_id TEXT,
  related_user_id TEXT,
  comment_level TEXT,
  parent_id TEXT,
  comment_timestamp TEXT,
  comment_votes TEXT,
  comment_text TEXT,
  top_parent_id TEXT
);
