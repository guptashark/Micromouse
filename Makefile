run:
	python2 tester.py maze_gen_output_02.txt
	python2 tester.py maze_gen_output_04.txt
	python2 tester.py maze_gen_output_05.txt 
	python2 tester.py maze_gen_output_06.txt
	python2 tester.py maze_gen_output_07.txt
	python2 tester.py maze_gen_output_08.txt
	python2 tester.py maze_gen_output_09.txt
	python2 tester.py maze_gen_output_10.txt


gen_maze:
	python2 maze_generator.py 
	python2 showmaze.py maze_gen_output_10.txt

tester: 
	python2 tester.py test_maze_01.txt 
	python2 tester.py test_maze_02.txt 
	python2 tester.py test_maze_03.txt



show:
	python2 showmaze.py test_maze_01.txt
