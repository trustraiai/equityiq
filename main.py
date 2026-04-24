from workflows.pipeline import run_pipeline

from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    result = run_pipeline("RELIANCE")
    print(result)