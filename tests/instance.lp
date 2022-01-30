

max_class_size(10).
min_class_size(2).


% can abstract classrooms away, by considering School buildings and their
% capacities (in simultaneous classes that can be held there = #rooms)
% building(name, rooms)
building(limmatplatz, 2).
building(altstetten, 2).


% student(name, niveau, schulgewohnt)
student(s1, (a0, sg)).
student(s2, (a0, sg)).

% teacher(name, min_shifts, max_shifts,
% 				teach_in(limmatplatz, altstetten),
%					can_teach(schulgewohnt, schulungewohnt),
%					available morning
%					available afternoon)
teacher(t1, 2,5, y,y, y,y, y,y,y,n,n, y,y,y,y,y).
