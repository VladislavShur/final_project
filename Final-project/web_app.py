"""Full Web Application Server for the CLI Suite.

Serves an interactive single-page dashboard with REST API endpoints:
- Task & Team Tracker
- Asset & License Tracker
- Test Log Analyzer & Statistics
Separated clean architecture: HTML template + static CSS + static JS.
Runs natively with standard library.
"""

import json
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import sys

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# ייבוא המודולים הקיימים
import task01
import asset_tracker
import log_storage
from analyzer_service import LogAnalyzerService

PORT = 8080
log_service = LogAnalyzerService()

# נתיבים לתבניות וקבצים סטטיים
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# טעינה ראשונית בטוחה
task01.load_tasks()


class WebRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _serve_file(self, file_path: Path):
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404, "File not found")
            return

        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = "text/plain"

        self.send_response(200)
        self.send_header("Content-Type", f"{mime_type}; charset=utf-8")
        self.end_headers()
        with open(file_path, "rb") as f:
            self.wfile.write(f.read())

    def do_GET(self):
        url = urlparse(self.path)
        path = url.path

        # דף הבית (HTML)
        if path in ("/", "/index.html"):
            index_path = TEMPLATES_DIR / "index.html"
            self._serve_file(index_path)
            return

        # קבצים סטטיים (CSS / JS)
        if path.startswith("/static/"):
            rel_path = path[len("/static/"):]
            static_file = (STATIC_DIR / rel_path).resolve()
            # מניעת Path Traversal
            if str(static_file).startswith(str(STATIC_DIR.resolve())):
                self._serve_file(static_file)
            else:
                self.send_error(403, "Forbidden")
            return

        # API: Tasks
        if path == "/api/tasks":
            task01.load_tasks()
            self._send_json({"tasks": task01.tasks})
            return

        # API: Assets
        if path == "/api/assets":
            assets = asset_tracker.load_assets()
            self._send_json({"assets": assets})
            return

        # API: Assets Report
        if path == "/api/assets/report":
            asset_tracker.export_report_core()
            report_text = ""
            if asset_tracker.REPORT_PATH.exists():
                report_text = asset_tracker.REPORT_PATH.read_text(encoding="utf-8")
            self._send_json({"success": True, "content": report_text})
            return

        # API: Logs
        if path == "/api/logs":
            if not log_service.is_loaded:
                self._send_json({"loaded": False})
                return
            stats = log_service.compute_statistics()
            entries = [{
                "timestamp": e.timestamp,
                "test_name": e.test_name,
                "status": e.status,
                "duration_sec": e.duration_sec,
                "severity": e.severity,
                "message": e.message
            } for e in log_service.entries]
            self._send_json({
                "loaded": True,
                "stats": {
                    "total_tests": stats.total_tests,
                    "passed_count": stats.passed_count,
                    "failed_count": stats.failed_count,
                    "avg_duration_sec": stats.avg_duration_sec,
                    "pass_rate_pct": stats.pass_rate_pct
                },
                "entries": entries
            })
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        url = urlparse(self.path)
        path = url.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b""
        payload = json.loads(body.decode("utf-8")) if body else {}

        # Add Task
        if path == "/api/tasks":
            name = payload.get("name", "").strip()
            if not name:
                self._send_json({"success": False, "error": "Task name is required"}, status=400)
                return
            task01.tasks.append({
                "name": name,
                "test_suite": payload.get("test_suite", "General"),
                "priority": payload.get("priority", "Medium"),
                "status": payload.get("status", "Pending")
            })
            task01.save_and_exit()
            self._send_json({"success": True})
            return

        # Assign Asset
        if path == "/api/assets/assign":
            asset_name = payload.get("asset_name", "").strip()
            employee = payload.get("employee", "").strip()
            category = payload.get("category", "Hardware")
            ok, msg = asset_tracker.assign_asset_core(asset_name, employee, category)
            if ok:
                self._send_json({"success": True, "message": msg})
            else:
                self._send_json({"success": False, "error": msg}, status=400)
            return

        # Return Asset
        if path == "/api/assets/return":
            asset_name = payload.get("asset_name", "").strip()
            ok, msg = asset_tracker.return_asset_core(asset_name)
            if ok:
                self._send_json({"success": True, "message": msg})
            else:
                self._send_json({"success": False, "error": msg}, status=400)
            return

        # Load Sample Logs
        if path == "/api/logs/sample":
            sample_path = BASE_DIR / "sample_test_logs.csv"
            if sample_path.exists():
                count = log_service.load_file(sample_path)
                self._send_json({"success": True, "count": count})
            else:
                self._send_json({"success": False, "error": "Sample file not found"}, status=404)
            return

        self.send_error(404, "Not Found")

    def do_PUT(self):
        url = urlparse(self.path)
        if url.path == "/api/tasks/status":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length > 0 else b""
            payload = json.loads(body.decode("utf-8")) if body else {}

            idx = payload.get("index")
            new_status = payload.get("status")
            if idx is not None and 0 <= idx < len(task01.tasks):
                task01.tasks[idx]["status"] = new_status
                task01.save_and_exit()
                self._send_json({"success": True})
            else:
                self._send_json({"success": False, "error": "Invalid index"}, status=400)
            return
        self.send_error(404, "Not Found")

    def do_DELETE(self):
        url = urlparse(self.path)
        if url.path == "/api/tasks":
            qs = parse_qs(url.query)
            idx_list = qs.get("index")
            if idx_list and idx_list[0].isdigit():
                idx = int(idx_list[0])
                ok, msg = task01.delete_task_core(idx)
                if ok:
                    self._send_json({"success": True, "message": msg})
                else:
                    self._send_json({"success": False, "error": msg}, status=400)
                return
            self._send_json({"success": False, "error": "Valid index is required"}, status=400)
            return
        self.send_error(404, "Not Found")


def run_server(port=PORT):
    server = HTTPServer(("0.0.0.0", port), WebRequestHandler)
    print(f"🚀 Operations & QA Web Application running on http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
