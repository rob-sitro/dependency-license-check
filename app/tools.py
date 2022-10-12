import os
import re
import json


supported_languages = os.environ.get(
    "SUPPORTED_LAGUAGES", ["ruby", "node", "python"])


def check_config_files(config):
    apps = config["apps"]
    errors = []
    allowed_licenses_file = config["allowed_licenses_file"]
    dependency_exceptions_file = config["dependency_exceptions_file"]

    if not os.path.exists(allowed_licenses_file):
        errors.append("allowed_license_file required but not found")

    if not os.path.exists(dependency_exceptions_file):
        errors.append("dependency_exceptions_file required but not found")
    
    for app in apps:
        for app_name, app_config in app.items():
            license_file = app_config["license_file"]
            language = app_config["language"]
            dependency_file = app_config["dependency_file"]
            
            err = is_language_supported(language)
            if err: errors.append(err)
            
            for f in [license_file, dependency_exceptions_file, dependency_file]:
                if not os.path.exists(f): errors.append("{} required but not found".format(f))
                        
    return errors
                        
                        
def is_language_supported(language):
    if language not in supported_languages:
        return "{} not a supported languaage at this time".format(language)
    
    return ""


def check_for_violations(license_data, allowed_licenses_file, dependency_exceptions_file):
    violations = []
    exceptions = []
    unknown_licenses = []

    with open(allowed_licenses_file) as f:
        a = json.load(f)
        allowed_licenses = [item.lower() for item in a]

    with open(dependency_exceptions_file) as f:
        dependency_exceptions = json.load(f)

    for env, dependencies in license_data.items():
        for dependency in dependencies:
            for dependency_name, license_list in dependency.items():
                license_names = get_license_names(license_list)

                for license_name in license_names:
                    if license_name.lower() in allowed_licenses:
                        break
                    else:
                        reason = find_exception(dependency_exceptions, dependency_name)
                        if reason:
                            print(" ##### Violation found but explicitly excepted. Dependency name: {},  License name: {}, Reason: {} ##### ".format(
                                dependency_name, license_name, reason))
                            exceptions.append({dependency_name: {"license_name": license_name, "exception_reason": reason}})
                            continue

                        if license_name.lower() == "unknown":
                            print(" ##### Unknown license for a dependency found . Dependency name: {},  License name: {} ##### ".format(dependency_name, license_name))
                            unknown_licenses.append({dependency_name: license_name})
                            continue

                    violations.append({dependency_name: license_name})
            
    return violations, exceptions, unknown_licenses


def get_license_names(license_list):
    parsed_licenses = []

    if type(license_list) == list:
        for lic in license_list:
            if type(lic) == str:
                if "and" in lic.lower():
                    n = lic.strip("(").strip(")")
                    parsed_licenses.append(n)
                    break
                if "or" in lic.lower():
                    parsed_licenses = lic.lower().split("or")
                    parsed_licenses = [s.replace("(", "") for s in parsed_licenses]
                    parsed_licenses = [s.replace(")", "") for s in parsed_licenses]
                    parsed_licenses = [s.strip() for s in parsed_licenses]
                    break
                
                parsed_licenses = license_list

    elif type(license_list) == bool:
        parsed_licenses = [str(license_list)]
        
    return parsed_licenses


def find_exception(dependency_exceptions, dependency_name):
    for exception_name, exception_reason in dependency_exceptions.items():
        exception_name = exception_name.replace("*", "." )
        rex = re.compile(exception_name)
        if dependency_name.startswith("@"):
            dependency_name = dependency_name[1:]

        dn = dependency_name.lower().split("@", 1)[0]

        if rex.findall(dn):
            return exception_reason
        
    return None

