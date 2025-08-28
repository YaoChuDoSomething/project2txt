import subprocess

def run_command(command):
    """Runs a shell command and returns its output."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Command: {command}\nOutput:\n{result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}\nError:\n{e.stderr}")
        return None

def automate_git_push():
    """Automates git add, commit, and push."""
    # Get the current branch name
    branch_name = run_command("git rev-parse --abbrev-ref HEAD")
    if not branch_name:
        print("Could not determine current branch. Aborting.")
        return
    branch_name = branch_name.strip() # Remove leading/trailing whitespace/newlines

    # Stage all changes
    print("Staging all changes...")
    if run_command("git add .") is None:
        print("git add . failed. Aborting.")
        return

    # Commit changes with a default message
    commit_message = "Automated commit"
    print(f"Committing with message: \"{commit_message}\"..." ) # Corrected escaping for the commit message string
    if run_command(f'git commit -m "{commit_message}"') is None:
        print("git commit failed. Aborting.")
        return

    # Push to the current branch on origin
    print(f"Pushing to origin/{branch_name}...")
    if run_command(f"git push origin {branch_name}") is None:
        print("git push failed. Aborting.")
        return

    print("Git automation complete!")

if __name__ == "__main__":
    automate_git_push()
