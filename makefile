make: app.py
	#xd

run: make
	python app.py

clean:
	rm -rf *~
	rm -rf *\#
