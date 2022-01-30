

max_class_size(10).
min_class_size(3).


% can abstract classrooms away, by considering School buildings and their
% capacities (in simultaneous classes that can be held there = #rooms)
% building(name, rooms)
building(limmatplatz, 1).
building(altstetten, 1).


% student(name, niveau, schulgewohnt)
student(s1, (a0, sg)).
student(s2, (a0, sg)).
student(s3, (a0, sg)).
student(s4, (a0, sg)).
student(s5, (a0, sg)).
student(s6, (a0, sg)).
student(s7, (a0, sg)).
student(s8, (a0, sg)).
student(s9, (a0, sg)).
student(s10, (a0, sg)).
student(s11, (a0, sg)).
student(s12, (a0, sg)).

student(s13, (a1, ug)).
student(s14, (a1, ug)).
student(s15, (a1, ug)).
student(s16, (a1, ug)).

student(s17, (a1, sg)).
student(s18, (a1, sg)).
student(s19, (a1, sg)).
student(s20, (a1, sg)).
student(s21, (a1, sg)).
student(s22, (a1, sg)).
student(s23, (a1, sg)).
student(s24, (a1, sg)).


% teacher(name, min_shifts, max_shifts,
% 				teach_in(limmatplatz, altstetten),
%					can_teach(schulgewohnt, schulungewohnt),
%					available morning
%					available afternoon)
teacher(t1, 4,10, y,n, y,y, y,y,y,n,n, y,y,y,y,y).
teacher(t2, 6,6, y,n, y,y, n,n,n,y,y, y,y,y,y,y).
teacher(t3, 4,10, n,y, y,y, y,y,y,n,n, y,y,y,n,n).
teacher(t4, 4,10, n,y, y,y, y,y,y,y,y, n,n,n,y,y).
