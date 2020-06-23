#!/bin/bash
W=$1
WN=$(echo $W|sed "s/ /-/g")
WGET="wget -q"
CACHE=$(dirname $0)/cambridge_cache
CAMBRIDGE=$(dirname $0)/cambridge.sh
AUDIO=$CACHE/${WN}.mp3

if [ ! -e "$AUDIO" ]; then
    if $CAMBRIDGE "$W" > /dev/null 2>&1; then
	URL="https://dictionary.cambridge.org/"$($CAMBRIDGE "$W" | tail -1)
	$WGET -O "$AUDIO" "$URL"
    else
	exit 1
    fi
fi
mplayer -quiet "$AUDIO" > /dev/null 2>&1
