gen_maze:
	python2 maze_generator.py 
	python2 showmaze.py maze_gen_output_10.txt

tester: 
	python2 tester.py test_maze_01.txt 
	python2 tester.py test_maze_02.txt 
	python2 tester.py test_maze_03.txt



show:
	python2 showmaze.py test_maze_01.txt
