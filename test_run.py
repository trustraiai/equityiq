import time
from workflows.pipeline import run_pipeline
from langchain_core.tools import Tool

from dotenv import load_dotenv
load_dotenv()

def test_stock(stock):
    print(f"\n🔍 Testing: {stock}")
    start = time.time()

    try:
        result = run_pipeline(stock)
        print("\n✅ Result:\n")
        print(result)

    except Exception as e:
        print(f"\n❌ Error for {stock}: {e}")

    end = time.time()
    print(f"\n⏱ Time taken: {round(end - start, 2)} sec")
    print("\n" + "="*100)

if __name__ == "__main__":
    stocks = ["RELIANCE"]

    for stock in stocks:
        test_stock(stock)