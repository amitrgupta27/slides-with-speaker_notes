[![Build Status](https://travis-ci.com/csci-e-29/2019sp-final-project-amitathex.svg?token=YpstnYB7tw1ULhZ529zy&branch=master)](https://travis-ci.com/csci-e-29/2019sp-final-project-amitathex)

# 2019sp-final-project-amitathex

## Src code
All the source is in one file under src/final-project/tasks.py. The code makes extensive use of ExternalProgramTask.

For project overview:

Slides: 
FinalProject-AmitRGupta.pdf

Recording:
https://drive.google.com/file/d/1JgjWNNW8X4NZ_1LUDv3YO-TAmNSOaG5E/view?usp=sharing

## Command line

```bash
# Please note you will need external program ffmpeg
brew install ffmpeg
OR
download static build from http://ffmpeg.org/download.html

# download lecture.mp4 from https://drive.google.com/open?id=1LmvoOxFViiAluapaSGTHJLuzvdLx1ciz
# Place lecture.mp4 into data/lecture directory

# In repo:
luigi --module final_project.tasks MapTextToSlides  --local-scheduler --lecture-duration seconds

# Scott's lectures were typically about 1:45 mins (6300 secs)
# luigi --module final_project.tasks MapTextToSlides  --local-scheduler --lecture-duration 6300

```

## Result

The above command line will generate a mapping of spoken text to slide number under data/mapping/mapfile.txt

Result is in the following format. 

Slide number followed by spoken text

SLIDE1

00:00:00 all right good evening welcome back from spring break a fun-filled events I assume I hope you enjoyed the last piece set of something that I was having a lot of fun with myself over for my Christmas break when I was first player on that stuff

00:00:20 and I thought it would be an appropriate way to play around with with Luigi so I hope that you enjoyed that and are able to finish that tonight without much further the difficulty we are going to continue into desk and Park

00:00:40 a little bit before the the midterm and we're really going to get started on it now I think it's a fascinating topic that really kind of helps evolve how you do big data science at least within python

00:01:00 Elsa helps understand somebody high-level objectives that we're talking about I'm in terms of storage mechanism just getting into the aspect of it as well as the the daggs in understanding your work as a graphical workflow

00:01:20 one thing that I wanted to point out is that I think there's been a few misses in terms of communication so Piazza is where we convey as a group on and student feedback between each other is Great Sands

00:01:40 is that are visible to everyone I think it's working pretty well for that but we haven't been super successful in Direct Communications on on Piazza Messina number post where people try to contact you know a specific TA or they ask for grading feedback and because there's so much stuff on Piazza

SLIDE2

00:02:00 in a formal way it's easy for us to to lose that and it's nothing personal we're not trying to snub anyone is it's just we're not all necessarily on Piazza in a dedicated fashion Andrew treated more like a group Collective where you know we get approximately everything

00:02:20 good at handling dreka news with communication so yes that you do that type of communication on do Canvas right so if you need to make an appointment for office hours you to send a direct message to another person that you're trying to contact on canvas if you have a question about your your grade on a particular thing use the the

00:02:40 I meant to discuss that our if you have overall questions on on grading either use the direct messages on canvas to do that that's something that'll no sense to look at your emails and we can you know reply more specifically

00:03:00 there's a little bit of distributed responsibility sometimes that happens there because none of us are quite sure who's been conversing with an individual student and who's really on point not for that that communication so please try to be direct on canvas we need that type of thing and let's just try to keep Piazza

00:03:20 visible posts for group discussion on I think that will it will help ensure that the communication standards remain I released the next step for the final project so hopefully you got some good inspiration

00:03:40 what are the bonus lectures that that we got out to you so that was Rihanna's work the week before the midterm and then we had Aaron and Joanna present their projects on the midterm election if you were taking the midterm and didn't get a chance to to see that Bunch material

SLIDE3

...
## Assumptions
The SpeechToText task assumes you have a internet connection. The wav to text is done via google clould API.


## Limitations

The image processing tasks (CropFrames) assumes Scott's lecture format where slides show up 
in the same top right hand side of the screen. 

Refer to slide number 5 in 
https://drive.google.com/file/d/1BVVmtdMYBaVqpqqjYbmBujxfCBPtSeUs/view?usp=sharing

SpeechToText is using free google service. For longer duration lectures (greater than 30 mins), I observed significant
throttling and slow down. One may need to move to paid Google service for production quality. 

## TODO

Generate a new annotated slide pdf from data/mapping/mapfile.txt 
