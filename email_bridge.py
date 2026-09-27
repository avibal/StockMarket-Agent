import smtplib
import sys
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config.config import Config

def markdown_to_html_email(md: str) -> str:
    """
    Converts standard and Telegram-style Markdown text into visually stunning,
    responsive HTML with professional RTL formatting for email clients.
    """
    if not md:
        return ""
        
    # 1. Escape HTML special characters for safety
    html = md
    html = html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # 2. Beautify horizontal rules
    html = html.replace("━━━━━━━━━━━━━━━━━━━━", "<hr style='border: 0; border-top: 2px solid #e2e8f0; margin: 20px 0;' />")
    
    # 3. Format standard code blocks ```json ... ```
    html = re.sub(
        r'```(?:json)?\n(.*?)\n```', 
        r'<pre style="direction: ltr; text-align: left; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; font-family: monospace; font-size: 13px; overflow-x: auto; color: #334155; margin: 16px 0;">\1</pre>', 
        html, 
        flags=re.DOTALL
    )
    
    # 4. Format inline code `code`
    html = re.sub(
        r'`([^`]+)`', 
        r'<code style="direction: ltr; background-color: #f1f5f9; border-radius: 4px; padding: 3px 6px; font-family: monospace; font-size: 13px; color: #0f172a; border: 1px solid #e2e8f0;">\1</code>', 
        html
    )
    
    # 5. Format double asterisks (**bold**) and single asterisks (*bold*)
    html = re.sub(r'\*\*([^*]+)\*\*', r'<strong style="color: #0f172a;">\1</strong>', html)
    html = re.sub(r'\*([^*]+)\*', r'<strong style="color: #0f172a;">\1</strong>', html)
    
    # 6. Format bullets nicely
    html = html.replace("• ", "<li style='margin-bottom: 8px; color: #334155;'>")
    
    # 7. Convert newlines to HTML line breaks
    html = html.replace("\n", "<br />")
    
    return html

def send_email_report(subject: str, report_markdown: str) -> bool:
    """
    Establishes secure SMTP TLS connection and sends a visually premium HTML
    financial report to the designated receiver email address.
    """
    # Verify email configurations are active
    is_valid, missing = Config.validate_email()
    if not is_valid:
        print(f"[!] Warning: Email Bridge disabled. Missing variables in .env: {missing}", file=sys.stderr)
        return False
        
    print(f"[+] Formatting strategic email report for dispatch...")
    
    # Assemble MIME envelope
    msg = MIMEMultipart()
    msg['From'] = Config.EMAIL_SENDER
    msg['To'] = Config.EMAIL_RECEIVER
    msg['Subject'] = subject
    
    # Convert markdown analysis to styled HTML
    html_content = markdown_to_html_email(report_markdown)
    
    # Wrap in premium CSS card layout
    email_body = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>{subject}</title>
      </head>
      <body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 680px; margin: 40px auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05); border-top: 8px solid #10b981;">
          <tr>
            <td style="padding: 40px; direction: rtl; text-align: right;">
              <!-- Header Brand -->
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 24px;">
                <tr>
                  <td style="font-size: 24px; font-weight: 800; color: #0f172a;">
                    📈 Stock Market AI Agent
                  </td>
                </tr>
                <tr>
                  <td style="font-size: 13px; color: #64748b; padding-top: 4px;">
                    דוח אנליסט פיננסי אוטומטי - פוזיציות וניהול סיכונים
                  </td>
                </tr>
              </table>
              
              <!-- Content Block -->
              <div style="font-size: 15px; line-height: 1.7; color: #334155;">
                {html_content}
              </div>
              
              <!-- Footer Details -->
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 40px; border-top: 1px solid #f1f5f9; padding-top: 20px;">
                <tr>
                  <td style="font-size: 12px; color: #94a3b8; text-align: center; line-height: 1.5;">
                    נשלח על ידי מערכת הניתוח האוטומטית שלך.<br />
                    שמור על אבטחת פרטי החשבון והפוזיציות הפיננסיות שלך.
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(email_body, 'html', 'utf-8'))
    
    # Connect and transmit securely
    try:
        print(f"[+] Connecting to SMTP server {Config.EMAIL_SMTP_SERVER}:{Config.EMAIL_SMTP_PORT}...")
        with smtplib.SMTP(Config.EMAIL_SMTP_SERVER, Config.EMAIL_SMTP_PORT) as server:
            server.starttls()  # Upgrade connection to secure TLS
            server.login(Config.EMAIL_SENDER, Config.EMAIL_PASSWORD)
            server.sendmail(Config.EMAIL_SENDER, [Config.EMAIL_RECEIVER], msg.as_string())
        print(f"[+] Successfully sent rich-text report to email: {Config.EMAIL_RECEIVER}!")
        return True
    except Exception as e:
        print(f"[-] Email transmission failed: {e}", file=sys.stderr)
        return False
