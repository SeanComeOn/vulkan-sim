def read_env_file(filepath):
    env_vars = {}
    with open(filepath, 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                env_vars[key] = value
    return env_vars

def compare_env_files(file1, file2):
    env1 = read_env_file(file1)
    env2 = read_env_file(file2)

    new_vars = {key: value for key, value in env2.items() if key not in env1 or env1[key] != env2[key]}
    return new_vars

def main():
    file1 = 'org.sh'
    file2 = 'later.sh'

    new_vars = compare_env_files(file1, file2)

    with open('new_vars.sh', 'w') as file:
        for key, value in new_vars.items():
            file.write(f'{key}={value}\n')

    print("New variables from later.sh have been written to new_vars.sh")

if __name__ == "__main__":
    main()