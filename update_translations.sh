#! /bin/bash

pot_file=i18n/onshape.pot

rm -f $pot_file
cp $pot_file.header $pot_file

for python_file in `find src/ -iname "*.py"`; do
	echo "Extract translations from" $python_file
	xgettext --from-code=UTF-8 --add-location=never --language=python --no-wrap --join-existing -ki18n:1 -ki18nc:1c,2 -ki18np:1,2 -ki18ncp:1c,2,3 $python_file -o $pot_file
done

for qml_file in `find resources/qml/ -iname "*.qml"`; do
	echo "Extract translations from" $qml_file
	xgettext --from-code=UTF-8 --add-location=never --language=javascript --no-wrap --join-existing -ki18n:1 -ki18nc:1c,2 -ki18np:1,2 -ki18ncp:1c,2,3 $qml_file -o $pot_file
done

for language_dir in `ls i18n`; do
	if [ -d "i18n/$language_dir" ]; then
		echo "Update language $language_dir"
		language_file="i18n/$language_dir/onshape.po"
		msgmerge --add-location=never --no-wrap --no-fuzzy-matching --update $language_file $pot_file
	fi
done
