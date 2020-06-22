A tool for learning vocabularies.

This tool will pick vocabularies randomly from new-words.txt, play
sound files from cambridge.org, and show definitions.

# USAGE

Run the following command to start the tool.  It will show a
vocabulary on the screen.

> $ ./learn-words.sh

Everytime you press 'ENTER' key, it picks another vocabulary from
new-words.txt for you.

## PRONUNCIATION

Pressing 'a' key, it will play the audio file of the current
vocabulary.  You can play the pronunciation as many times as you like.

Running the tool with the "-a" parameter, it will play pronunciations
automatically.

## DEFINITION

Pressing 'd' key, it will show the definition of the current
vocabulary.

## TAG and UNTAG

Pressing 't' key, the current vocabulary will be added to tagged-words.txt.
Pressing 'T' key, the current vocabulary will be remove from tagged-words.txt.

By maintaining tagged-words.txt, you can revise only vocabularies in
this file by running the following command.

> $ ./learn-words.sh -t

## REINFORCE

For some vocabularies, you want to learn them more often than others.

Pressing 'r' key, the current vocabulary will be added to reinforce-words.txt.
Pressing 'T' key, the current vocabulary will be removed from reinforce-words.txt.

The vocabularies in reinforce-words.txt have higher chance to be picked by the tool.

By default, every 20 times, it will show one reinforced vocabulary in average.
It can be changed by passing a "-r" parameter.

> $ ./learn-words.sh -r 15  # one reinforced vocabulary every 15 times.

## NEW VOCABULARIES

You can query the definition of a new word whenever you want by
starting with ":" and following with the vocabulary.

For example, the following sequence is to check the definition of "monkey".

> :monkey

The vocabulary will be added to new-words.txt too.

# VOCABULARIES FROM FIREFOX

You can extract vocabularies that you have asked to cambridge.org or
several other sites from the history databse of firefox with the
following command.

> $ ./firefox-history.py -t

It will show a list of vocabularies.  You can start with adding the
list to new-words.txt.
