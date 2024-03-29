#! /bin/bash

for language_dir in `ls i18n`; do
	if [ -d "i18n/$language_dir" ]; then
		echo "Make binary language file $language_dir"
		language_file="i18n/$language_dir/onshape.po"
		msgfmt "i18n/$language_dir/onshape.po" -o "i18n/$language_dir/LC_MESSAGES/onshape.mo" -v
	fi
done
