import os
import sys
import re
import string

import pyclan as pc


subr_rgx = re.compile("timestamp adjusted: was (\d+)")
subr_rgx2 = re.compile("(starts|ends) at (\d+).")

interval_regx = re.compile("\\x15\d+_\d+\\x15")


def pull_timestamps(path):
    stamps = []
    with open(path, "rU") as input:
        lines = []

        # last line was start of subregion comment, but timestamp
        # was not on that line. need to check following line
        # due to multiline wrapping of comments. this variable
        # keeps track of how many lines back the start of the
        # subregion comment was (it's a negative number so you
        # can index back into the lines[], e.g.:
        #
        #       lines[last_was_subr:])
        #
        last_was_subr = 0

        for i, line in enumerate(input):
            if "subregion" in line:
                was = subr_rgx.findall(line)
                start = subr_rgx2.findall(line)
                if was and len(was) == 1 and start and len(start) == 1:
                    # print was[0]
                    stamps.append((was[0], start[0][1]))
                    lines.append(line)
                    continue
                else:
                    last_was_subr -= 1
                    lines.append(line)
                    continue
            else:
                if last_was_subr < 0:
                    # combine previous line with this line
                    l = lines[last_was_subr:] + [line]
                    new_line = join_lines(l)

                    was = subr_rgx.findall(new_line)
                    start = subr_rgx2.findall(new_line)
                    if was and len(was) == 1 and start and len(start) == 1:
                        last_was_subr = 0
                        stamps.append((was[0], start[0][1]))
                        lines.append(line)
                        continue
                    else:
                        last_was_subr -= 1
                        lines.append(line)
                        if last_was_subr < -3:
                            raise Exception("couldn't find the end")
                        continue
                else:
                    lines.append(line)

    if len(lines) != i + 1:
        raise Exception("missing lines")
    return stamps


def join_lines(lines):
    subr_line = " ".join(lines)
    table = string.maketrans("\t\n", "  ")
    new_line = subr_line.translate(table)
    new_line = new_line.replace("   ", " ")
    new_line = new_line.replace("  ", " ")
    return new_line


def rewrite_stamps(in_path, out_path, stamps):
    proc_idx = 0
    olds = [stamps[y][0] for y in range(len(stamps))]
    with open(in_path, "rU") as input:
        with open(out_path, "wb") as out:
            for i, line in enumerate(input):
                # if proc_idx > len(stamps) - 1:
                #     out.write(line)

                # found_ts = False
                if any("_{}".format(x) in line for x in olds):
                    for x in olds:
                        if "_{}".format(x) in line:
                            idx = olds.index(x)
                            m = interval_regx.findall(line)
                            if m and len(m) == 1:
                                out.write(line.replace(
                                    stamps[idx][0], stamps[idx][1]))
                                # proc_idx += 1
                            else:
                                out.write(line)




                # elif any(x in line for x in olds):
                #     m = interval_regx.findall(line)
                #     if m and len(m) == 1:
                #         out.write(line.replace(
                #             stamps[proc_idx][0], stamps[proc_idx][1]))
                #         proc_idx += 1
                #     else:
                #         out.write(line)
                # if not found_ts:
                else:
                    out.write(line)


if __name__ == "__main__":

    input_dir = sys.argv[1]
    out_dir = sys.argv[2]

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".cha"):
                print file
                in_path = os.path.join(root, file)
                out_path = os.path.join(out_dir, file)

                stamps = pull_timestamps(in_path)
                rewrite_stamps(in_path, out_path, stamps)
