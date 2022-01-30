"""Script to run ASP ground and solve."""

from clingo.control import Control
import click
import os

def csv_to_atoms(path, sep=';', with_header=True):
    """Return list of strings, each string is an atom corresponding to
    a line in the csv file.
    If with_header is true, the first line is a comment explaining each
    field."""
    def line_to_atom(line):
        return f"{atom_name}({','.join(line.rstrip().split(sep))})"
    
    atom_name = os.path.basename(path)
    with open(path, 'r') as f:
        atoms = list(map(line_to_atom, f))        
        if with_header:
            atoms[0] = f"% {atoms[0]}"
    return atoms
            




@click.command()
@click.argument('teacher_file')
@click.argument('students_file')
@click.argument('rooms_file')
@click.option("--min_class_size", default=3)
@click.option("--max_class_size", default=10)
@click.option("-k", "--keep_instance_file", is_flag=True, default=True)
def main(teacher_file,
         students_file,
         rooms_file,
         min_class_size,
         max_class_size,
         keep_instance_file):


    best_model = {"classes": None, "teacher_shifts": None}
    def store_model(model):
        """Takes a clingo.solving.Model and extracts the 
        assign_student_class and assign_shift_teacher atoms."""
        syms = model.symbols(atoms=True)
        classes = {}
        teacher_shifts = {}
        for sym in syms:
            if sym.match("assign_student_class", 4):
                name, place, room, time = sym.arguments
                class_id = (place.name, room.number, time.name)
                if class_id not in classes:
                    classes[class_id] = []
                classes[class_id].append(name.name)
            elif sym.match("assign_shift_teacher", 5):
                name, place, room, day, time = sym.arguments
                teacher = name.name
                if teacher not in teacher_shifts:
                    teacher_shifts[teacher] = []
                teacher_shifts[teacher].append((
                    place.name, room.number, day.name, time.name
                ))
        best_model["classes"] = classes
        best_model["teacher_shifts"] = teacher_shifts

    def write_model_csv(solve_result):
        day_time_to_idx_name = {
            ("mon", "am"): {"name": "Mon AM", "idx": 0},
            ("mon", "pm"): {"name": "Mon PM", "idx": 1},
            ("tue", "am"): {"name": "Tue AM", "idx": 2},
            ("tue", "pm"): {"name": "Tue PM", "idx": 3},
            ("wed", "am"): {"name": "Wed AM", "idx": 4},
            ("wed", "pm"): {"name": "Wed PM", "idx": 5},
            ("thu", "am"): {"name": "Thu AM", "idx": 6},
            ("thu", "pm"): {"name": "Thu PM", "idx": 7},
            ("fri", "am"): {"name": "Fri AM", "idx": 8},
            ("fri", "pm"): {"name": "Fri PM", "idx": 9},
        }
        with open("teacher_shifts.csv", "w") as f:
            names = [dt["name"] for dt in day_time_to_idx_name.values()]
            f.write("Teacher;"+";".join(names)+"\n")
            for teacher, shifts in best_model["teacher_shifts"].items():
                assigned_on_day = ["" for dt in day_time_to_idx_name]
                for place,room,day,time in shifts:
                    assigned_on_day[day_time_to_idx_name[(day,time)]["idx"]] = f"{place}/{room}"
                f.write(teacher + ";" + ";".join(map(str, assigned_on_day)) + "\n")
        with open("classes.csv", "w") as f:
            f.write("Place;Room;Time;" + ";".join([
                f"student{i}" for i in range(1,max_class_size+1)
            ]) + "\n")
            for class_id, students in best_model["classes"].items():
                place,room,time = class_id
                f.write(f"{place};{room};{time};" + ";".join(students) + "\n")
                
            
    
    INSTANCE_FNAME = "instance_file.lp"
    
    # if os.path.exists(INSTANCE_FNAME):
    #     print("instance_file.lp exists. exiting...")
    #     exit(1)

    # # write instance file from csv
    # with open(INSTANCE_FNAME, "w") as f:
    #     for inf in [teacher_file, students_file, rooms_file]:
    #         for atom in csv_to_atoms(inf):
    #             f.write(atom)
    #             f.write("\n")
    #         f.write("\n")
        
    ctl = Control(arguments=[
        #"outf=3", # silent
        "--opt-mode=opt", # optimize costs
    ])

    ctl.load("encoding.lp")
    ctl.load(INSTANCE_FNAME)

    ctl.ground([("base", [])])
    ctl.solve(
        on_model=store_model,
        on_finish=write_model_csv
    )

    if not keep_instance_file:
        os.remove(INSTANCE_FNAME)
    


if __name__ == '__main__':
    main()
