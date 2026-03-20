import time
from urllib.parse import urlencode
from flask import json, request, current_app as app
from flask import Flask
import os
from dotenv import load_dotenv, find_dotenv
from playwright.sync_api import sync_playwright
import logging
import traceback

load_dotenv(find_dotenv())

def create_app():
    app = Flask(__name__)

    @app.route('/watershed/<int:id>/report/pdf', methods=['POST'])
    def render_vue_page(id):
        """
        Using parameters, display a watershed static report page
        populated with all of the report contents and printed in a view-friendly format

        Query Parameters:
            id (int) Watershed Feature Id
        """
        pdf_bytes = None
        user_data = json.loads(request.data)
        # set the wfi from the path
        user_data['wfi'] = id
        with sync_playwright() as p:
            try:
                gpu_args = [
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ]
                # Launch the browser in 'headed' mode to see the UI, or 'headless=True' for background operation
                browser = p.chromium.launch(headless=True, args=gpu_args)
                context = browser.new_context(
                    ignore_https_errors=True,
                    bypass_csp=True,
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
                )
                page = context.new_page()

                customization_json = user_data['userCustomization']

                def wait_for_section_load(section_id):
                    js_predicate = f"""
                        () => {{ return document.{section_id}Loaded === true; }}
                    """
                    page.wait_for_function(js_predicate)

                # Navigate to your locally running Vue application URL
                static_url = f"{os.getenv('CLIENT_URL')}/watershed/static-report"
                page.goto(static_url)

                page.evaluate(f"window.user_data = {json.dumps(user_data)};")
                page.evaluate(f"window.customization_json = {json.dumps(customization_json)};")

                # Wait for the page to be fully interactive (Playwright has built-in auto-waiting)
                for section in customization_json["sections"]:
                    try:
                        print(section)
                        # if(section != "reportCover" and section != "annualHydrology"):
                        wait_for_section_load(section)
                        print(f"{section} Loaded!")
                    except Exception as e:
                        print(f"Timeout waiting for section {section} to load: {e}")
                        raise e

                pdf_bytes = page.pdf(
                    path=None,
                    display_header_footer=True,
                    header_template='<span></span>',
                    footer_template=f"""
                        <div style="display: flex; justify-content: space-around; font-size:8px; text-align: center; width: 100%; margin: 0 10px;">
                        <div class="date"></div><div>Page <span class="pageNumber"></span> of <span class="totalPages"></span></div><div>WFI: {id}</div>
                        </div>
                    """
                )
                return pdf_bytes
            except Exception as e:
                traceback.format_exc()
                raise Exception({
                    "user_message": "Error generating the PDF. Please try again later",
                    "server_message": e,
                    "status_code": 500
                })

    @app.errorhandler(Exception)
    def handle_error(error):
        message = "Internal Server Error"
        status_code = 500
        try:
            server_message = " - ERROR - " + str(error)
        except Exception as e:
            server_message = " - ERROR - " + str(error)
        if len(error.args) > 0 and type(error.args[0]) is dict:
            if 'user_message' in error.args[0]:
                message = error.args[0]["user_message"]
            if 'status_code' in error.args[0]:
                status_code = error.args[0]['status_code']
            if 'server_message' in error.args[0]:
                try:
                    server_message = " - ERROR - " + error.args[0]['server_message']
                except Exception:
                    server_message = " - ERROR - " + str(error)
        logging.error(server_message)
        return { "message" : message }, status_code

    return app

if __name__ == '__main__':
    app.run(debug=True)
