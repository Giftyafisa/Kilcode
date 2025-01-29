FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=8000
ENV DATABASE_URL=postgresql://neondb_owner:SXTcliLd3P2t@ep-aged-paper-a9nahjyk.gwc.azure.neon.tech/neondb?sslmode=require
ENV ADMIN_DATABASE_URL=postgresql://neondb_owner:SXTcliLd3P2t@ep-patient-hall-a9zlztc2.gwc.azure.neon.tech/neondb?sslmode=require
ENV SECRET_KEY=K_ela_Tony
ENV ENVIRONMENT=production
ENV API_V1_STR=/api/v1
ENV ADMIN_SECRET_KEY=K_ela_Tony
ENV ADMIN_TOKEN_EXPIRE_MINUTES=1440
ENV PAYMENT_ADMIN_TOKEN_EXPIRE_MINUTES=1440
ENV ALLOWED_ORIGINS=https://kilcode-admin.vercel.app,https://admin-ten-silk.vercel.app,https://backend-mu-seven-60.vercel.app,https://kilcode-frontend.vercel.app,http://localhost:5173,http://localhost:5174
ENV PAYSTACK_SECRET_KEY=sk_test_9c8ed29806799887814242571899edf82071ac09
ENV PAYSTACK_PUBLIC_KEY=pk_test_7f3cabce055cc9cb562103752d9348c39d7fde9b
ENV PAYSTACK_SECRET_KEY_GHS=sk_test_9c8ed29806799887814242571899edf82071ac09
ENV PAYSTACK_PUBLIC_KEY_GHS=pk_test_7f3cabce055cc9cb562103752d9348c39d7fde9b
ENV PAYSTACK_SECRET_KEY_NGN=sk_test_9c8ed29806799887814242571899edf82071ac09
ENV PAYSTACK_PUBLIC_KEY_NGN=pk_test_7f3cabce055cc9cb562103752d9348c39d7fde9b

# Expose the port the app runs on
EXPOSE ${PORT}

# Command to run the application
CMD python -c "import os; port = int(os.getenv('PORT', 8000)); from app.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=port)" 