#/bin/bash

for D in *; do
    if [-d "${D}]; then
        LEN=$(echo "${D}"")
        if {$LEN -eq "20"]; then
            echo "Randomly genera 20 character Arta repo detected, repo name ${D}"
        fi
    fi
done
