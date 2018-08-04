#!/bin/bash

repos=(docker-web docker-homebridge docker-homekit2mqtt docker-mail2url docker-rsyslog docker-vpn docker-unifi)
use_key=0

function init {
    cwd=`pwd`
    if [ $1 -eq 1 ]; then
        git_url="git@github.com:bzzeke"
    else
        git_url="https://github.com/bzzeke"
    fi

    for repo in ${repos[@]}; do
        if [ ! -d $cwd/$repo ]; then
            git clone $git_url/$repo.git
        fi
    done
}

function update {
    cwd=`pwd`

    for repo in ${repos[@]}; do
        printf "\nUpdating $repo...\n"
        cd $cwd/$repo
        git fetch origin
        git stash
        git rebase origin/master
        git stash pop
    done
    cd $cwd
}

while getopts k flag
do
    case $flag in
        k)
            use_key=1
            ;;
        ?)
            exit
            ;;
    esac
done

shift $(( OPTIND - 1 ))

if [ $1 ]; then
    case $1 in
        init)
            init $use_key
            ;;
        update)
            update
            ;;
        *)
            echo "command not found"
            ;;
    esac
else
    echo "No command passed"
fi
