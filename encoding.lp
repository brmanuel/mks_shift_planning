
% compute an assignment of students to classes
% and of teachers to shifts

% fix definitions
day(
	mon;
	tue;
	wed;
	thu;
	fri).


time(
	am;
	pm).


%% transform
class(B, I, T) :- I=1..M, building(B,M), time(T).

teacher_name(T) :-             teacher(T,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_).

can_teach_at(T,limmatplath) :- teacher(T,_,_,y,_,_,_,_,_,_,_,_,_,_,_,_,_).
can_teach_at(T,altstetten) :-  teacher(T,_,_,_,y,_,_,_,_,_,_,_,_,_,_,_,_).

can_teach_niveau(T, sg) :-     teacher(T,_,_,_,_,y,_,_,_,_,_,_,_,_,_,_,_).
can_teach_niveau(T, ug) :-     teacher(T,_,_,_,_,_,y,_,_,_,_,_,_,_,_,_,_).
														   
available_at(T, mon, am) :-    teacher(T,_,_,_,_,_,_,y,_,_,_,_,_,_,_,_,_).
available_at(T, tue, am) :-    teacher(T,_,_,_,_,_,_,_,y,_,_,_,_,_,_,_,_).
available_at(T, wed, am) :-    teacher(T,_,_,_,_,_,_,_,_,y,_,_,_,_,_,_,_).
available_at(T, thu, am) :-    teacher(T,_,_,_,_,_,_,_,_,_,y,_,_,_,_,_,_).
available_at(T, fri, am) :-    teacher(T,_,_,_,_,_,_,_,_,_,_,y,_,_,_,_,_).
														   
available_at(T, mon, pm) :-    teacher(T,_,_,_,_,_,_,_,_,_,_,_,y,_,_,_,_).
available_at(T, tue, pm) :-    teacher(T,_,_,_,_,_,_,_,_,_,_,_,_,y,_,_,_).
available_at(T, wed, pm) :-    teacher(T,_,_,_,_,_,_,_,_,_,_,_,_,_,y,_,_).
available_at(T, thu, pm) :-    teacher(T,_,_,_,_,_,_,_,_,_,_,_,_,_,_,y,_).
available_at(T, fri, pm) :-    teacher(T,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,y).

niveau(N) :- student(_,N).

%% generate

% each class has a niveau
{ assign_niveau_class(N,B,I,T) : niveau(N) } = 1 :- class(B,I,T).

% each student has a class of their niveau
{ assign_student_class(S,B,I,T) : class(B,I,T), assign_niveau_class(N,B,I,T) } = 1
	:- student(S,N).

% each shift with students has exactly one teacher
{ assign_shift_teacher(N,B,I,D,T) : teacher_name(N) } = 1 :-
	class(B,I,T), day(D),
	#count { S : assign_student_class(S,B,I,T) } > 0.
	
%% test (hard constraints)

% don't assign more than two teachers to same class
:- class(B,I,T),
	 #count { N : assign_shift_teacher(N,B,I,_,T) } > 2.

% only assign one shift at a time to a teacher
:- assign_shift_teacher(N,B1,I1,D,T),
	 assign_shift_teacher(N,B2,I2,D,T),
	 (B1,I1) < (B2,I2).

% plan teachers on days when they're available 
:- assign_shift_teacher(N,_,_,D,T),
	 not available_at(N,D,T).


%% optimize (soft constraints)

% only assign niveau the teacher can teach
:~ assign_shift_teacher(N,B,I,D,T),
	 assign_niveau_class((_,SGUG),B,I,T),
	 not can_teach_niveau(N, SGUG).
	 [ 1@3, N,B,I,D,T]

% class size
:~ not L <= #count { S : assign_student_class(S,B,I,T) } <= U,
	 class(B,I,T),
	 min_class_size(L),
	 max_class_size(U).
	 [ 1@2, B,I,T]
	 
% only assign teachers to shifts they like
:~ assign_shift_teacher(T,B,_,D,T),
	 not can_teach_at(T,B).
	 [ 1@1, T,B,D,T]

:~ teacher(N,L,U,_,_,_,_,_,_,_,_,_,_,_,_,_,_),
	 not L <= #count { B,I,D,T : assign_shift_teacher(N,B,I,D,T) } <= U.
	 [ 1@1, N]


%% show
#show assign_shift_teacher/5.
#show assign_student_class/4.
