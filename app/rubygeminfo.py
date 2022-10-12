import requests
import json


def licenses(dependency_file, app_name, license_file):
    licenses = {}

    gem_names = parse_gemfile(dependency_file)

    print("Finding licenses for gems in runtime...")

    lics = get_licenses(gem_names, license_file)
    licenses["runtime"] = lics        
    
    return licenses


def parse_gemfile(dependency_file):
    deps = []
    full_deps = []
    with open(dependency_file) as f:
        lines = [line.strip() for line in f]

    hit = False
    for line in lines:
        if "specs:" in line:
            hit = True

        if "PLATFORMS" in line:
            hit = False

        if hit is True:
            if "specs:" in line:
                continue
            elif "PLATFORMS" in line:
                continue
            elif not line:
                continue

            deps.append(line)

    for dep in deps:
        split_dep = dep.split(" ", 1)
        if len(split_dep) > 1:
            dep_name = split_dep[0]
            dep_version = split_dep[1]
            if dep_version[1].isdigit():
                full_deps.append("{}@{}".format(dep_name, dep_version[1:-1]))

    return full_deps


def get_licenses(gem_names, license_file):
    licenses = []
    
    with open(license_file) as f:
        dependency_data = json.load(f)
            
    for gem_name in gem_names:
        license = dependency_data.get(gem_name)
        if license:
            licenses.append({gem_name: license})
        else:
            print("{} not found in database. fetching from rubygems.org...".format(gem_name))
            license = fetch_license(gem_name)
            licenses.append({gem_name: license})
            if license:
                add_gem_to_license_file(gem_name, license, license_file)
            
    return licenses


def fetch_license(lock_gem_name):
    gem_name = lock_gem_name.split("@")[0]
    gem_version = lock_gem_name.split("@")[1]

    r = requests.get(
        'https://rubygems.org/api/v2/rubygems/{}/versions/{}.json'.format(gem_name, gem_version))
    
    if r.status_code != 200:
        print("error retrieving {} license. skipping adding to licenses.json.".format(gem_name))
        return ["unknown"]
    
    data = r.json()

    if not data.get("licenses"):
        print("[WARN] No license info found for {}".format(gem_name))
        return "unknown"
    
    return data.get("licenses")


def add_gem_to_license_file(gem_name, license, license_file):
    with open(license_file,'r+') as file:
        file_data = json.load(file)
        file_data[gem_name] = license
        file.seek(0)
        json.dump(file_data, file, indent = 4)


 