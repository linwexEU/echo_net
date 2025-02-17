from email.message import EmailMessage 
from pydantic import EmailStr 


def create_reset_password_confirmation_template(to_: EmailStr, from_: EmailStr, pin_code: int, ip: str, device: str, browser: str): 
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EchoNet - PIN Code</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f3f4f6;
                margin: 0;
                padding: 0;
                text-align: center;
            }}
            .container {{
                background-color: #ffffff;
                max-width: 400px;
                margin: 40px auto;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background-color: #059669;
                color: white;
                padding: 10px;
                font-size: 20px;
                font-weight: bold;
            }}
            .pin {{
                font-size: 22px;
                font-weight: bold;
                background-color: #e5e7eb;
                padding: 10px;
                border-radius: 5px;
                display: inline-block;
                margin: 10px 0;
            }}
            .info {{
                font-size: 14px;
                color: #4b5563;
                margin-top: 10px;
            }}
            .footer {{
                background-color: #1f2937;
                color: white;
                font-size: 12px;
                padding: 8px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="header">EchoNet</div>
        
        <div class="container">
            <h2>Your PIN Code for changing password</h2>
            <div class="pin">{pin_code}</div>
            
            <div class="info">
                <p><strong>IP:</strong> {ip}</p>
                <p><strong>Device:</strong> {device}</p>
                <p><strong>Browser:</strong> {browser}</p>
                <p>If you didn't request a password reset, ignore this email.</p>
            </div>
        </div>

        <div class="footer">
            &copy; 2025 EchoNet. All rights reserved.
        </div>
    </body>
    </html>
    """

    email = EmailMessage() 

    # Set content 
    email.set_content(html_content, subtype="html")

    email["Subject"] = "EchoNet: Pin Code for password change!"
    email["From"] =  from_
    email["To"] = to_

    return email
