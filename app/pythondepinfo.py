import requests
import json
import requirements

def licenses(dependency_file, app_name, license_file):
    dependencies = {}
    
    with open(dependency_file) as f:
        dep_names = []
        for req in requirements.parse(f):
            
            if not req.specs:
                dep_version = "latest"
            elif req.specs[0][0] == "==":
                dep_version = req.specs[0][1]
            else:
                print("unable to parse requirements.txt file")
                exit(1)
            
            dep_names.append("{}@{}".format(req.name, dep_version))

    dependencies["production"] = dep_names
        
    licenses = get_licenses(dependencies, license_file)
    
    return licenses
    

def get_licenses(dependencies, license_file):
    full_deps = {}
    
    with open(license_file) as f:
        dependency_data = json.load(f)
        
    for env, deps in dependencies.items():
        licenses = []
        for dep_lock_version in deps:
            dep_name = dep_lock_version.split("@")[0]
            dep_version = dep_lock_version.split("@")[1]
            license = dependency_data.get(dep_lock_version)
            if license:
                licenses.append({dep_lock_version: license})
            else:
                print("{} not found in database. fetching from pypi.org...".format(dep_lock_version))
                license = fetch_license(dep_name, dep_version)
                if license:
                    add_dep_to_license_file(dep_lock_version, license, license_file)
                licenses.append({dep_lock_version: license})
        full_deps[env] = licenses  
        
    return full_deps


def fetch_license(dep_name, dep_version):
    if dep_version == "latest":
        r = requests.get(
            'https://pypi.org/pypi/{}/json'.format(dep_name))
    else:
        r = requests.get(
            'https://pypi.org/pypi/{}/{}/json'.format(dep_name, dep_version))
    
    if r.status_code != 200:
        print("error retrieving {}@{} license. skipping adding to licenses.json.".format(
            dep_name, dep_version))
        return ["unknown"]
    
    data = r.json()

    lic = data.get("info").get("license")

    if not lic:
        print("[WARN] No license info found for {}@{}".format(dep_name, dep_version))
        return ["unknown"]
    
    return [lic]


def add_dep_to_license_file(dep_name, license, license_file):
    with open(license_file,'r+') as file:
        file_data = json.load(file)
        file_data[dep_name] = license
        file.seek(0)
        json.dump(file_data, file, indent = 4)
