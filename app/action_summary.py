import os

def create(license_violations, license_exceptions, unknown_depedency_licenses, all_dependencies):
        
    with open ("job_summary.md", "w") as f:
        f.write("# Dependency Check Summary \n")
        f.write(" --- \n")
        f.write("### License Violations\n")
        f.write("")
        f.write("")
        if not license_violations:
            f.write("#### No license violations found\n\n")
        else:
            f.write("| App Name | Language | Dependency Name | License Name\n")
            f.write("| ------ | ------ | ------ | ------ | \n")
            for violation in license_violations:
                f.write("| {} | {} | {} | {} |\n".format(
                    violation["app_name"], violation["language"], 
                    violation["dependency_name"], violation["license_name"]
             ))

        f.write("### Unknown dependency licenses\n")
        f.write("")
        f.write("")
        if not unknown_depedency_licenses:
            f.write("#### No unknown dependency licenses\n\n")
        else:
            f.write("| App Name | Language | Dependency Name | License Name\n")
            f.write("| ------ | ------ | ------ | ------ | \n")
            for unknown_license in unknown_depedency_licenses:
                f.write("| {} | {} | {} | {} |\n".format(
                    unknown_license["app_name"], unknown_license["language"], 
                    unknown_license["dependency_name"], unknown_license["license_name"]
             ))
                
        f.write("\n### Dependencies Not Included In Check\n")
        f.write("")
        f.write("")
        f.write("| App Name | Language | Dependency Name | License Name | Reason\n")
        f.write("| ------ | ------ | ------ | ------ | ------ | \n")
        for exception in license_exceptions:
            f.write("| {} | {} | {} | {} | {} \n".format(
                exception["app_name"], exception["language"], 
                exception["dependency_name"], exception["license_name"], exception["exception_reason"]
        ))
                
        f.write("\n### All Checked Dependencies\n")
        f.write("")
        f.write("")
        f.write("| App Name | Language | Dependency Name | License Name |\n")
        f.write("| ------ | ------ | ------ | ------ | \n")
        for dependencies in all_dependencies:
            app_name = dependencies["app_name"]
            language = dependencies["language"]
            license_data = dependencies["license_data"]
            for env, deps in license_data.items():
                for dep in deps:
                    for dep_name, license_name in dep.items():
                        f.write("| {} | {} | {} | {} |\n".format(
                            app_name, language, 
                            dep_name, license_name
                        ))

    with open("job_summary.md", "r")  as fr:
        os.environ["GITHUB_STEP_SUMMARY"] = fr.read()
        
    print("Job summary report created {}".format(os.path.abspath("job_summary.md")))
     