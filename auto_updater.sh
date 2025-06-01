#!/bin/bash 

# Created by OneKnown
#This will check OS package manager then run the update process


for pm in apt dpkg rpm yum dnf pacman snap flatpak zypper port emerge slackpkg apk guix nix; do
    if [[ -x $(command -v $pm) ]];then
        echo "found $pm"
        sudo $pm update -y && $pm upgrade -y
        break
    fi
done

