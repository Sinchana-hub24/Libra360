.PHONY: help floci-up floci-down backend-install backend-start frontend-install frontend-start setup-librarian run

help:
	@echo "Library360 targets"
	@echo "  make floci-up        Start local GCP emulator (floci-gcp)"
	@echo "  make backend-install Install Python backend dependencies"
	@echo "  make backend-start   Start FastAPI backend"
	@echo "  make frontend-install Install frontend dependencies"
	@echo "  make frontend-start  Start React frontend"
	@echo "  make setup-librarian Create initial librarian account"
	@echo "  make run              Start emulator, backend, and frontend"

floci-up:
	docker run -d --name floci-gcp -p 4588:4588 \
		-e FLOCI_GCP_STORAGE_MODE=hybrid \
		-v floci-gcp-data:/app/data \
		floci/floci-gcp:latest

floci-down:
	docker stop floci-gcp
	docker rm floci-gcp

backend-install:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install fastapi "uvicorn[standard]" pydantic pydantic-settings \
		google-cloud-firestore google-cloud-storage PyJWT python-multipart

backend-start:
	set -a && . ./.env && set +a && .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000

frontend-install:
	cd Library360_Frontend && npm install

frontend-start:
	cd Library360_Frontend && PATH=/tmp/opencode/node/bin:$$PATH nohup npm run dev > /tmp/opencode/library360-frontend.log 2>&1 & echo "frontend pid $$!"

setup-librarian:
	curl -sS -X POST http://127.0.0.1:8000/auth/setup-librarian \
		-H "Content-Type: application/json" \
		-H "X-Setup-Secret: library360-setup-dev" \
		-d '{"full_name":"Library Admin","email":"admin@library360.local","password":"AdminPassword123!"}'

run:
	@docker rm -f floci-gcp 2>/dev/null || true
	@docker run -d --name floci-gcp -p 4588:4588 \
			-e FLOCI_GCP_STORAGE_MODE=hybrid \
			-v floci-gcp-data:/app/data \
			floci/floci-gcp:latest;
	@if pgrep -f "uvicorn app.main:app" > /dev/null 2>&1; then \
		echo "Backend already running on http://127.0.0.1:8000"; \
	else \
		set -a && . ./.env && set +a && nohup .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 > /tmp/opencode/library360-backend.log 2>&1 & echo "backend pid $$!"; \
	fi
	@if pgrep -f "vite" > /dev/null 2>&1; then \
		echo "Frontend already running on http://127.0.0.1:5173"; \
	else \
		cd Library360_Frontend && PATH=/tmp/opencode/node/bin:$$PATH nohup npm run dev > /tmp/opencode/library360-frontend.log 2>&1 & echo "frontend pid $$!"; \
	fi
	@echo "Library360 backend starting on http://127.0.0.1:8000"
	@echo "Library360 frontend starting on http://127.0.0.1:5173"
