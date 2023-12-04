#!/bin/sh

echo ""
echo "Loading azd .env file from current environment"
echo ""

while IFS='=' read -r key value; do
    value=$(echo "$value" | sed 's/^"//' | sed 's/"$//')
    export "$key=$value"
done <<EOF
$(azd env get-values)
EOF

if [ $? -ne 0 ]; then
    echo "Failed to load environment variables from azd environment"
    exit $?
fi

echo 'Creating python virtual environment "backend/backend_env"'
python3 -m venv backend/backend_env

echo ""
echo "Restoring backend python packages"
echo ""

cd backend
./backend_env/bin/python -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to restore backend python packages"
    exit $?
fi

echo ""
echo "Restoring frontend npm packages"
echo ""

cd ../frontend
npm install
if [ $? -ne 0 ]; then
    echo "Failed to restore frontend npm packages"
    exit $?
fi
echo ""
echo "Starting frontend in development mode"
echo ""

cd ../frontend

# Start the frontend development server in the background
npm run dev &

FRONTEND_PID=$!

echo ""
echo "Starting backend"
echo ""

cd ../backend

port=50505
host=localhost
./backend_env/bin/python -m quart --app main:app run --port "$port" --host "$host" --reload &

BACKEND_PID=$!

# Wait for either process to exit
wait $FRONTEND_PID $BACKEND_PID