import requests
import json


def licenses(dependency_file, app_name, license_file):
    
    with open(dependency_file) as f:
        dependency_dictionary = json.load(f)

    if dependency_dictionary.get("lockfileVersion") == 2:
        dependencies = parse_v2_lock_file(dependency_dictionary)
    elif dependency_dictionary.get("lockfileVersion") == 1:
        dependencies = parse_v1_lock_file(dependency_dictionary)
    else:
        print("unable to parse node package-lock.json file. valid lock file required")
        exit(1)
    
    licenses = get_licenses(dependencies, license_file)
        
    return licenses


def parse_v2_lock_file(dependency_dictionary):
    dependencies = {}

    packages = dependency_dictionary.get("packages")
    packages_key = next(iter(packages))
    dev_dependencies = packages[packages_key].get("devDependencies")
    prod_dependencies = packages[packages_key].get("dependencies")

    dependencies["development"] = dev_dependencies
    dependencies["production"] = prod_dependencies

    return dependencies


def parse_v1_lock_file(dependency_dictionary):
    dependencies = {}
    d = {}

    packages = dependency_dictionary.get("dependencies")
    for package_name, package_metadata in packages.items():
        version = package_metadata.get("version")
        d[package_name] = version

    dependencies["production"] = d

    return dependencies


def get_licenses(dependencies, license_file):
    full_deps = {}
    
    with open(license_file) as f:
        dependency_data = json.load(f)
        
    for env, deps in dependencies.items():
        licenses = []
        print("Finding licenses for dependencies in {}...".format(env))
        for dep_name, dep_version in deps.items():
            dep_version = dep_version.strip("^")
            dep_lock_version = "{}@{}".format(dep_name, dep_version)
            license = dependency_data.get(dep_lock_version)
            if license:
                licenses.append({dep_lock_version: license})
            else:
                print("{} not found in database. fetching from registry.npmjs.org...".format(dep_lock_version))
                license = fetch_license(dep_name, dep_version)
                licenses.append({dep_lock_version: license})
                if license:
                    add_dep_to_license_file(dep_lock_version, license, license_file)
        full_deps[env] = licenses
                
    return full_deps


def fetch_license(dep_name, dep_version):
    r = requests.get(
        'https://registry.npmjs.org/{}/{}'.format(dep_name, dep_version))
    
    if r.status_code != 200:
        print("error retrieving {}@{} license. skipping adding to licenses.json.".format(
            dep_name, dep_version))
        return ["unknown"]
    
    data = r.json()

    if not data.get("license"):
        print("[WARN] No license info found for {}@{}".format(dep_name, dep_version))
        return ["unknown"]
    
    return [data.get("license")]


def add_dep_to_license_file(dep_name, license, license_file):
    with open(license_file,'r+') as file:
        file_data = json.load(file)
        file_data[dep_name] = license
        file.seek(0)
        json.dump(file_data, file, indent = 4)

