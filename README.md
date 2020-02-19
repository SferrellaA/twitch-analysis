# Influence Operations on Twitch.tv?

In this repository is the code used in a yet-unpublished paper currently undergoing peer review. This readme will be expanded upon approval/rejection by the journal.

To quote from the paper on what this code does:
>1. A data structure was created that associates a commenter’s username with the number of comments they wrote. That is, by providing a given number, such as 3, one received a list of all users that wrote 3 comments.
>2. A data structure was generated that associates a commenter’s username to his or her average and range of comment speed (in milliseconds). That is, by providing a username, one received that user’s average and range of comment speed.
>    * Average comment speed was defined as the average number of milliseconds between all the users’ comments.
>    * Range of comment speed was defined as the difference between the longest and shortest time between the user’s comments. To calculate this, only users with at least three comments were considered. Comment speed range was not used in this study, but could be used in future iterations.
>3. The mean and median comment __count__ of each stream was then calculated. Due to the nature of Twitch’s platform, most streams have right-skewed count distributions. That is, most users write very few comments, and a few users write so many comments that they bring the stream’s comment count mean above the median.
>    * Mean comment count was defined as the average number of comments posted by users. Users that only watched a stream but did not comment were not considered in the results. 
>    * Median comment count was defined as the middlemost count of comments posted by users.
>4. The mean and median comment __speed__ of each stream was then calculated.
>    * Mean comment speed was defined as the average of the users’ comment speeds calculated earlier (only users with at least three comments).
>    * Median comment speed was defined as the middlemost of the users’ comment speeds calculated earlier.
>5. The stream was considered anomalous if users were commenting in greater volume and at greater speed than would be expected based upon the stream’s median comment count and comment speed. For this study, a value of 3 was used to establish significance; that is, a mean comment count at least three times the median comment count, or a mean comment speed at most one-third the median comment speed (in milliseconds). This was a subjective definition and can be adjusted for future studies by editing the _config.ini_ file.
>6. The users of an anomalous stream were then reviewed. If exhibiting anomalous behavior of their own, their comments were recorded for review by a human reviewer.
>    * Anomalous users were defined as users whose individual comment count was at least three times the stream’s median comment count and who had a mean comment speed at most one-third of the stream’s median comment speed.

