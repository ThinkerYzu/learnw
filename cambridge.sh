#!/bin/bash
W="$1"
D=$(dirname $0)
FETCHER="python $D/cambridge.py"
CACHE=$D/cambridge_cache

FUNC="SHOW"
if [ "$W" = "-d" ]; then
    FUNC="DEL"
    W="$2"
elif [ "$W" = "-D" ]; then
    FUNC="DEF"
    W="$2"
fi

WN=$(echo $W|sed "s/ /-/g")

DEFINITION=$CACHE/"$WN".txt

if [ "$FUNC" = "DEL" ]; then
    rm "$DEFINITION"
elif [ "$FUNC" = "DEF" ]; then
    if [ ! -e "$DEFINITION" ]; then
	$FETCHER "$W" > "$DEFINITION"
	if [ $? -ne 0 ]; then
	    rm "$DEFINITION"
	    echo "Error ..."
	    exit 1
	fi
    fi
    cat "$DEFINITION" | awk -- '/^[^: ].*/ { if (LAST_DEF) printf " "; printf "%s", $0; LAST_DEF=1} /^[: ]|^$/ {if (LAST_DEF) print ""; LAST_DEF=""}'
else
    if [ ! -e "$DEFINITION" ]; then
	$FETCHER "$W" > "$DEFINITION"
	if [ $? -ne 0 ]; then
	    rm "$DEFINITION"
	    echo "Error ..."
	    exit 1
	fi
    fi

    cat "$DEFINITION"
fi
