#!/bin/bash

#
# ProfitBricks API CLI auto-updater
#
# (C)2012, ProfitBricks GmbH
# support@profitbricks.com
#
# This program is launched by src/pbcli.py, you can launch it yourself if you want
# It returns exit code 1 if the application was updated, 0 otherwise (it's up-to-date or there was an error)
#

exit_code=0 # = 0 if nothing happened, = 1 if we updated
git_dir=''

if [ -d "$(dirname $(readlink -f $0))/.git" ]; then
	git_dir=$(dirname $(readlink -f $0))
elif [ -d "$(dirname $(readlink -f $0))/../.git" ]; then
	git_dir=$(dirname $(readlink -f $0))/..
fi

if [ "$git_dir" != "" ]; then # we have a ".git" directory
	pushd . >/dev/null
	cd "$git_dir"
	if [ "$(which git 2>&1 >/dev/null ; echo $?)" -eq "0" ]; then # we have the git application
		git pull | grep 'files changed' | grep 'insertions' | grep 'deletions'
		if [ "$?" -eq "0" ]; then
			exit_code=1
			rm -rf "test" >/dev/null
			echo -e "\n# WARNING: Please review the license file before continuing. The terms and conditions may have changed since the last update!\n"
		else
			echo "Already up-to-date."
		fi
	else
		echo 'Nothing to do (git not found)'
	fi
	popd >/dev/null
else
	echo 'Local git repository not found'
fi

exit $exit_code

# test
