#!/bin/bash
D=$(dirname $0)
NEW_WORDS=$D/new-words.txt
TAGGED_WORDS=$D/tagged-words.txt
REINFORCE_WORDS=$D/reinforce-words.txt
CAMBRIDGE=$D/cambridge.sh
CAMBRIDGE_AUDIO=$D/cambridge_audio.sh
NOTES_DIR=$D/word_notes/
SPEAK="FESTIVAL"
DEFLINES=60
REINFORCE_RATE=20
AUTO_SHOW_DEFINITION=
AUTO_PLAY_AUDIO=
STUDY_TAGGED=

function FESTIVAL() {
    echo "$1" | festival --tts
}

function show_help() {
    cat <<EOF
Usage: $(basename $0) [-adht] [-n <word-file>] [-r <reinforce-rate>]
  -a	play pronunciation of the traning word.
  -d	show automatically the definition of the training word.
  -h	show this help.
  -t    study only tagged words.
  -n <word-file>
	give the name file of training words.
  -r <reinforce-rate>
	give the rate of reinforcement learning.
	(In freq. of 1/<reinforce-rate>
EOF
}

eval set -- $(getopt -- adhn:r:t $@)
while true; do
    opt="$1"
    if [ "$opt" = "-d" ]; then
	AUTO_SHOW_DEFINITION=1
    elif [ "$opt" = "-a" ]; then
	AUTO_PLAY_AUDIO=1
    elif [ "$opt" = "-h" ]; then
	show_help
	exit 0
    elif [ "$opt" = "-n" ]; then
	NEW_WORDS="$2"
	shift
    elif [ "$opt" = "-t" ]; then
	STUDY_TAGGED=1
    elif [ "$opt" = "-r" ]; then
	REINFORCE_RATE="$2"
	shift
    else
	break
    fi
    shift
done

while true; do
    #
    # Pick the current studied word
    #
    if [ -n "$STUDY_TAGGED" ]; then
	REINFORCE=1		# never reinforce
	LINE=$(shuf $TAGGED_WORDS | tail -1)
        echo TAG
    else
	REINFORCE=$(python -c "import random; print random.randint(0, $REINFORCE_RATE-1)")
	if [ -e $REINFORCE_WORDS -a "$REINFORCE" = "0" ]; then
	    LINE=$(shuf $REINFORCE_WORDS|tail -1)
	    if [ -z "$LINE" ]; then
		continue
	    fi
	else
	    LINE=$(shuf $NEW_WORDS|tail -1)
            REINFORCE=1
	fi
    fi
    WORD=$(echo $LINE|awk -F ',' -- '{print $1;}')

    TAGGED=0
    if [ -e "$TAGGED_WORDS" ]; then
        if grep "$WORD" "$TAGGED_WORDS" > /dev/null 2>&1; then
            TAGGED=1
        fi
    fi

    if [ -n "$AUTO_SHOW_DEFINITION" ]; then
	clear
	APPEND=""
	if grep "$WORD" "$REINFORCE_WORDS" > /dev/null 2>&1; then
	    APPEND="$APPEND (R)"
	fi
	if [ -e "${NOTES_DIR}/${WORD}.txt" ]; then
	    APPEND="$APPEND (N)"
	fi
        if [ "$TAGGED" = "1" ]; then
            APPEND="$APPEND (T)"
        fi
	echo "$LINE$APPEND"
	if $CAMBRIDGE "$WORD" > /dev/null 2>&1; then
	    $CAMBRIDGE "$WORD" | head -${DEFLINES}
	else
	    echo "Definition is not found!"
	fi
    else
	clear
	if [ "$REINFORCE" = "0" ]; then
	    OUT="$LINE (R)"
	else
	    OUT="$LINE"
	fi
        if [ "$TAGGED" = "1" ]; then
            OUT="$OUT (T)"
        fi
        echo "$OUT"
    fi

    if [ -n "$AUTO_PLAY_AUDIO" ]; then
	$CAMBRIDGE_AUDIO "$WORD"
    fi
    
    while true; do
	read -n 1 -s FN
	if [ "$FN" = "d" ]; then
	    if $CAMBRIDGE "$WORD" > /dev/null 2>&1; then
		clear
		$CAMBRIDGE "$WORD" | head -${DEFLINES}
	    else
		echo "Network is error or the word is not found!"
	    fi
	elif [ "$FN" = "a" ]; then
	    echo "playing ..."
	    if ! $CAMBRIDGE_AUDIO "$WORD"; then
		echo "Error"
	    fi
	elif [ "$FN" = "A" ]; then
	    echo "Speak out the definition..."
	    if ! $CAMBRIDGE -D "$WORD" > /dev/null 2>&1; then
		echo "The definition is not found!"
	    else
		DEFINITION=$($CAMBRIDGE -D "$WORD" | head -2 | tail -1)
		$SPEAK "$DEFINITION"
	    fi
	elif [ "$FN" = "D" ]; then
	    $CAMBRIDGE -d "$WORD"
	    echo "Remove from cache"
	elif [ "$FN" = "r" ]; then
	    if ! grep "$WORD" $REINFORCE_WORDS > /dev/null 2>&1; then
		echo $WORD >> $REINFORCE_WORDS
		echo "Reinforce '$WORD'"
	    else
		echo "Already being reinforced"
	    fi
	elif [ "$FN" = "R" ]; then
	    if grep "$WORD" $REINFORCE_WORDS > /dev/null 2>&1; then
		grep -v "$WORD" "$REINFORCE_WORDS" > "${REINFORCE_WORDS}.bak"
		cat "${REINFORCE_WORDS}.bak" > "$REINFORCE_WORDS"
		rm "${REINFORCE_WORDS}.bak"
		echo "Not reinforce '$WORD' anymore"
	    else
		echo "Not being reinforced"
	    fi
	elif [ "$FN" = "t" ]; then
	    if ! grep "$WORD" $TAGGED_WORDS > /dev/null 2>&1; then
		echo $WORD >> $TAGGED_WORDS
		echo "Tag '$WORD'"
	    else
		echo "Already being tagged"
	    fi
	elif [ "$FN" = "T" ]; then
	    if grep "$WORD" $TAGGED_WORDS > /dev/null 2>&1; then
		grep -v "$WORD" "$TAGGED_WORDS" > "${TAGGED_WORDS}.bak"
		cat "${TAGGED_WORDS}.bak" > "$TAGGED_WORDS"
		rm "${TAGGED_WORDS}.bak"
		echo "Untag '$WORD'"
	    else
		echo "Not being tagged"
	    fi
	elif [ "$FN" = "q" ]; then
	    exit 0
	elif [ "$FN" = "N" ]; then
	    NOTE_FILE="${NOTES_DIR}/${WORD}.txt"
	    $EDITOR "$NOTE_FILE"
	    if [ -e "$NOTE_FILE" -a "$(stat -c %s $NOTE_FILE)" = "0" ]; then
		rm "$NOTE_FILE"
		echo "The note is just deleted!"
	    fi
	    echo $WORD
	elif [ "$FN" = "n" ]; then
	    NOTE_FILE="${NOTES_DIR}/${WORD}.txt"
	    if [ -e "$NOTE_FILE" ]; then
		echo "Note of '$WORD':"
		cat "$NOTE_FILE" | awk -- '{print "> "$0;}'
	    else
		echo "Having no note for '$WORD'"
	    fi
	elif [ -z "$FN" ]; then
	    break
	elif [ "$FN" = ':' ]; then
	    echo -n ':'
	    read W
	    if [ -z "$W" ]; then
		continue
	    fi
	    echo "Finding definition of '$W' ..."
	    if $CAMBRIDGE "$W" > /dev/null 2>&1; then
		$CAMBRIDGE "$W" | head -${DEFLINES}
		echo '...'
		if ! grep $W $NEW_WORDS > /dev/null; then
		    echo $W >> $NEW_WORDS
		fi
	    else
		echo 'Error'
	    fi
	fi
    done
done
