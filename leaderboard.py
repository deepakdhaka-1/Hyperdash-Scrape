from playwright.sync_api import sync_playwright
import json

def fetch_top_traders():
    with sync_playwright() as p:
        print("[DEBUG] Launching browser (headed mode)...")
        browser = p.chromium.launch(headless=False)  # Headed to solve Turnstile
        context = browser.new_context()
        page = context.new_page()

        top_traders_data = None

        # Intercept responses
        def handle_response(response):
            if "top-traders-cached" in response.url:
                try:
                    nonlocal top_traders_data
                    top_traders_data = response.json()
                    print("[DEBUG] Captured top traders JSON!")
                except Exception as e:
                    print("[ERROR] Failed to parse JSON:", e)

        page.on("response", handle_response)

        print("[DEBUG] Open the top-traders page in browser...")
        page.goto("https://hyperdash.info/top-traders")

        # Wait enough time to manually solve Turnstile and let API respond
        wait_time = 30000  # 30 seconds
        print(f"[DEBUG] Waiting {wait_time / 1000} seconds for you to solve Turnstile...")
        page.wait_for_timeout(wait_time)

        if top_traders_data:
            print("[DEBUG] Printing full JSON data:")
            print(json.dumps(top_traders_data, indent=4))

            # Save to leaderboard.json
            with open("leaderboard.json", "w", encoding="utf-8") as f:
                json.dump(top_traders_data, f, ensure_ascii=False, indent=4)
            print("[DEBUG] Data saved to leaderboard.json")
        else:
            print("[DEBUG] No data captured. Make sure Turnstile is solved and API responded.")

        print("[DEBUG] Done. Closing browser...")
        browser.close()

if __name__ == "__main__":
    fetch_top_traders()
