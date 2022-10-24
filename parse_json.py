import json
import os


def to_markdown_table(rows: list[dict]) -> str:
    if not rows:
        return ""

    headings = f'| {" | ".join(rows[0].keys())} |'
    heading_bottom = f'| {" --- | " * len(rows[0].keys())}'
    lines = [headings, heading_bottom]

    for d in rows:
        lines.append(f"| {' | '.join([str(v) for v in d.values()])} |")

    return "\n".join(lines)


def read_all_files(directory: str) -> dict:
    """
    Read all json files in directory and convert to dict. Map computer
    name (determined by file name) to that dict. Return the mapping.
    """
    computers = {}
    _, __, json_files = os.walk(directory).__next__()
    for file in json_files:
        with open(f"{directory}/{file}", "rb") as f:
            # "laser-blue" becomes "Laser Blue"
            name = file.split("_", 1)[0].replace("-", " ").title()
            computers[name] = json.load(f)

    return computers


def get_specs(computers: dict) -> list[dict]:
    """
    Extract desired information from computer information. Return a list
    of dicts containing that information.
    """
    # The keys we're interested in, and what we want to rename it as
    desired_information = [
        ("OsName", "OS"),
        ("CsPhyicallyInstalledMemory", "RAM"),  # MS spelled it wrong -_-
        ("ClockSpeed", "CPU"),
        ("CsUserName", "User Name"),
        ("OsRegisteredUser", "Registered User"),
        ("IP", "IP"),
    ]

    # Formatting changes to the values
    information_mutations = {
        "ClockSpeed": lambda x: f"{round(x / 1_000, 1)} MHz",
        "CsPhyicallyInstalledMemory": lambda x: f"{round(x / 1_000_000, 1)} GB",
    }

    # Extract all the keys we wanted and perform mutations
    all_specs = []
    for name, info in list(computers.items()):
        info["specs"]["full"] |= info["networking"]
        specs = {"Location": name}
        for key, rename in desired_information:
            specs[rename] = info["specs"]["full"][key]
            if key in information_mutations:
                specs[rename] = information_mutations[key](specs[rename])

        all_specs.append(specs)

    return all_specs


def get_installed_software(computers: dict, no_clutter=True) -> dict[str : list[dict]]:
    all_installed_software: dict[str : list[dict]] = {}
    for name, info in list(computers.items()):
        installed_software = info["installed_software"]

        if no_clutter:
            # Somewhat sloppy way of cleaning up the list so it's not cluttered
            # by drivers and runtimes. There could be false positives, but I
            # didn't see any.
            blacklisted_publishers = [
                "Advanced Micro Devices, Inc.",
                "NVIDIA Corporation",
                "Microsoft Corporation",
            ]
            installed_software = list(
                filter(
                    lambda d: d["publisher"] not in blacklisted_publishers,
                    installed_software,
                )
            )

        # Sort by publisher. Use a set to eliminate duplicates. Some are None, hence str(x)
        publishers = sorted(
            {d["publisher"] for d in installed_software}, key=lambda x: str(x)
        )

        # Map publishers to list of software
        publishers = {pub: [] for pub in publishers}
        for software in installed_software:
            publishers[software["publisher"]].append(software)

        # Map the computer name to the list of software
        for software_list in publishers.values():
            # sort the software for each publisher by name
            software_list.sort(key=lambda x: x["name"])
            # add all software for this publisher to the master list for this computer
            all_installed_software.setdefault(name, []).extend(software_list)

    return all_installed_software


def to_csv(computers: dict[str : list[dict]]) -> str:
    if not computers:
        return ""

    # Ugly way of grabbing what is currently the name/publisher/version keys.
    # We don't want to hardcode it in case we collect more data later.
    headers = ",".join(computers.values().__iter__().__next__()[0])
    lines = [f"computer,{headers}"]

    for name, rows in computers.items():
        for row in rows:
            line = [repr(name)]
            line.extend([repr(item) for item in row.values()])
            lines.append(",".join(line))

    return "\n".join(lines)


def main():
    computers = read_all_files("computer_information/")
    specs = get_specs(computers)
    installed_software = get_installed_software(computers)

    # Write the installed software to a CSV file
    os.makedirs("output", exist_ok=True)
    with open("output/installed_software.csv", "w") as f:
        # Include all the cruft in the CSV -- it could be useful.
        installed_software = get_installed_software(computers, no_clutter=True)
        csv_installed_software = to_csv(installed_software)
        f.write(csv_installed_software)

    print("# Specs")
    print(to_markdown_table(specs))

    lines = ["# Installed Software"]
    for name, software_list in installed_software.items():
        lines.append(f"## {name}")
        lines.append(to_markdown_table(installed_software[name]))

    with open("output/installed_software.md", "w") as f:
        f.writelines(lines)


if __name__ == "__main__":
    main()
