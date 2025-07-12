from pyngrok import ngrok, conf
from app import app
import os

# Kill any existing ngrok processes
ngrok.kill()

# Set auth token
conf.get_default().auth_token = "2zm2trRBl9BhevZqpX1VMuQlDdw_35aKHA3A7EHhz2sdHyNfo"

# Start ngrok with configuration file
tunnel = ngrok.connect(5000, domain="safe-proper-muskox.ngrok-free.app")
print('\n' + '='*50)
print('Ngrok Tunnel Established!')
print('Webhook URL (use this for GitHub):', 'https://safe-proper-muskox.ngrok-free.app/webhook')
print('='*50 + '\n')

# Run the app
if __name__ == '__main__':
    try:
        port = int(os.getenv('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    finally:
        ngrok.kill() 