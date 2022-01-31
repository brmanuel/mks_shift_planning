"""Script to run ASP ground and solve."""

from clingo.control import Control
import click
import os


def csv_to_atoms(path, atom_name, sep=';', with_header=True):
    """Return list of strings, each string is an atom corresponding to
    a line in the csv file.
    If with_header is true, the first line is a comment explaining each
    field."""
    def line_to_atom(line):
        return f"{atom_name}({','.join(line.rstrip().split(sep))})."

    with open(path, 'r') as f:
        atoms = list(map(line_to_atom, [l for l in f if l.strip()]))        
        if with_header:
            atoms[0] = f"% {atoms[0]}"
    return atoms

def class_atom_cb(symbol, model):
    name, place, room, time = symbol.arguments
    class_id = (place.name, room.number, time.name)
    if class_id not in model["classes"]:
        model["classes"][class_id] = []
    model["classes"][class_id].append(name.name)


def shift_atom_cb(symbol, model):    
    name, place, room, day, time = symbol.arguments
    teacher = name.name
    if teacher not in model["teacher_shifts"]:
        model["teacher_shifts"][teacher] = []
    model["teacher_shifts"][teacher].append((
        place.name, room.number, day.name, time.name
    ))

def store_soft_constr(symbol, model):
    model["soft_constraints"].append(str(symbol))
    
    
@click.command()
@click.argument('teacher_file')
@click.argument('students_file')
@click.argument('rooms_file')
@click.option("--min_class_size", default=3)
@click.option("--max_class_size", default=10)
@click.option("-k", "--keep_instance_file", is_flag=True, default=False)
def main(teacher_file,
         students_file,
         rooms_file,
         min_class_size,
         max_class_size,
         keep_instance_file):


    best_model = {"classes": None, "teacher_shifts": None, "soft_constraints": None}
    def store_model(model):
        """Takes a clingo.solving.Model and extracts the 
        assign_student_class and assign_shift_teacher atoms."""
                
        cb_map = {
            ("assign_student_class", 4): lambda sym: class_atom_cb(sym, best_model),
            ("assign_shift_teacher", 5): lambda sym: shift_atom_cb(sym, best_model),
            ("wrong_day_teacher", 3): lambda sym: store_soft_constr(sym, best_model),
            ("teacher_only_one_day", 4): lambda sym: store_soft_constr(sym, best_model),
            ("wrong_niveau_teacher", 5): lambda sym: store_soft_constr(sym, best_model),
            ("wrong_class_size", 3): lambda sym: store_soft_constr(sym, best_model),
            ("wrong_place_teacher", 4): lambda sym: store_soft_constr(sym, best_model),
            ("wrong_num_shifts_teacher", 1): lambda sym: store_soft_constr(sym, best_model),
        }
        syms = model.symbols(atoms=True)
        best_model["classes"] = {}
        best_model["teacher_shifts"] = {}
        best_model["soft_constraints"] = []
        
        for sym in syms:
            for (name, arity), callback in cb_map.items():
                if sym.match(name, arity):
                    callback(sym)
            

    def write_model_csv(solve_result):
        day_time_to_idx_name = {
            ("mon", "am"): {"name": "Mon AM", "idx": 0},
            ("tue", "am"): {"name": "Tue AM", "idx": 1},
            ("wed", "am"): {"name": "Wed AM", "idx": 2},
            ("thu", "am"): {"name": "Thu AM", "idx": 3},
            ("fri", "am"): {"name": "Fri AM", "idx": 4},
            ("mon", "pm"): {"name": "Mon PM", "idx": 5},
            ("tue", "pm"): {"name": "Tue PM", "idx": 6},
            ("wed", "pm"): {"name": "Wed PM", "idx": 7},
            ("thu", "pm"): {"name": "Thu PM", "idx": 8},
            ("fri", "pm"): {"name": "Fri PM", "idx": 9},
        }
        try:
            os.mkdir("output")
        except FileExistsError:
            pass
        
        with open(os.path.join("output", "teacher_shifts.csv"), "w") as f:
            names = [dt["name"] for dt in day_time_to_idx_name.values()]
            f.write("Teacher;"+";".join(names)+"\n")
            for teacher, shifts in best_model["teacher_shifts"].items():
                assigned_on_day = ["" for dt in day_time_to_idx_name]
                for place,room,day,time in shifts:
                    assigned_on_day[day_time_to_idx_name[(day,time)]["idx"]] = f"{place}/{room}"
                f.write(teacher + ";" + ";".join(map(str, assigned_on_day)) + "\n")
        with open(os.path.join("output", "classes.csv"), "w") as f:
            f.write("Place;Room;Time;" + ";".join([
                f"student{i}" for i in range(1,max_class_size+1)
            ]) + "\n")
            for class_id, students in best_model["classes"].items():
                place,room,time = class_id
                students += [""] * (max_class_size - len(students))
                f.write(f"{place};{room};{time};" + ";".join(students) + "\n")
        print("Violated Soft-constraints:")
        for constr in best_model["soft_constraints"]:
            print(constr)
                
                
    INSTANCE_FNAME = "instance_file.lp"
    
    if os.path.exists(INSTANCE_FNAME):
        print("instance_file.lp exists. exiting...")
        exit(1)

    # write instance file from csv
    with open(INSTANCE_FNAME, "w") as f:
        for inf,atom_name in [
                (teacher_file, "teacher"),
                (students_file, "student"),
                (rooms_file, "building")
        ]:
            for atom in csv_to_atoms(inf, atom_name):
                f.write(atom)
                f.write("\n")
            f.write("\n")
        f.write(f"max_class_size({max_class_size}).\n")
        f.write(f"min_class_size({min_class_size}).\n")

            
    ctl = Control(arguments=[
        "--opt-mode=opt", # optimize costs
    ])

    ctl.load("encoding.lp")
    ctl.load(INSTANCE_FNAME)

    ctl.ground([("base", [])])
    ctl.solve(
        on_model=store_model,
        on_finish=write_model_csv,
    )

    if not keep_instance_file:
        os.remove(INSTANCE_FNAME)
    


if __name__ == '__main__':
    main()
